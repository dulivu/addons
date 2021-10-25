# -*- coding: utf-8 -*-
import pytz
from datetime import datetime, timedelta
from odoo import models, fields, api


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    chkin_location_id = fields.Many2one('hr.geolocation', 'Ubicacion de Entrada')
    chkout_location_id = fields.Many2one('hr.geolocation', 'Ubicacion de Salida')

    def _get_resource_calendar_attendance(self, dt):
        resource_calendar_attendance = self.employee_id.calendar_id.attendance_ids.filtered(
            lambda x: x.dayofweek == str(dt.weekday()))
        return resource_calendar_attendance

    @api.multi
    def auto_checkout(self):
        for attendance in self:
            employee_id = attendance.employee_id
            if employee_id.calendar_id:
                dt = fields.Datetime.context_timestamp(self,
                                                       fields.Datetime.from_string(attendance.check_in))
                hour_to = attendance._get_resource_calendar_attendance(dt).hour_to
                hour_to = divmod((hour_to - 2) * 60, 60)
                td_chkin = timedelta(hours=dt.hour, minutes=dt.minute)
                td_chkout = timedelta(hours=int(hour_to[0]), minutes=int(hour_to[1]))
                if td_chkin > td_chkout:
                    attendance.check_out = attendance.check_in
                else:
                    check_out = dt.replace(hour=int(hour_to[0]), minute=int(hour_to[1]), second=0)
                    attendance.check_out = fields.Datetime.to_string(
                        check_out.astimezone(pytz.utc))
            else:
                attendance.check_out = attendance.check_in
