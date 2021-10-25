# -*- coding: utf-8 -*-

from odoo import models, fields, api

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def _float_to_timestring(self,pformat,ptime):
        if ptime < 0:
            return '-'+pformat.format(*divmod(abs(ptime) * 60, 60))
        else:
            return pformat.format(*divmod(ptime * 60, 60))

    @api.one
    def GetMyAttendances(self, date_start, date_end):
        data = []
        time_format = '{0:02.0f}:{1:02.0f}'
        my_attendances = self.env['hr.attendance'].search(
            [('check_in', '>=', date_start), ('check_in', '<=', date_end), ('employee_id', '=', self.id)])
        for attendance in my_attendances:
            values = {
                'id': attendance.id,
                'check_in': attendance.check_in,
                'chkin_time_diference': self._float_to_timestring(time_format,attendance.chkin_time_diference),
                'check_out': attendance.check_out,
                'chkout_time_diference': self._float_to_timestring(time_format,attendance.chkout_time_diference),
                'total_diference': self._float_to_timestring('{0:02.0f} h {1:02.0f} min',attendance.total_diference),
                'positive': True if attendance.total_diference > 0 else False,
            }
            # resource_calendar = attendance._get_resource_calendar_attendance(
            #     fields.Datetime.context_timestamp(self, fields.Datetime.from_string(attendance.check_in)))
            # if resource_calendar:
            #     hour_from = '{0:02.0f}:{1:02.0f}'.format(*divmod(resource_calendar.hour_from * 60, 60))
            #     hour_to = '{0:02.0f}:{1:02.0f}'.format(*divmod(resource_calendar.hour_to * 60, 60))
            # values['schedule'] = hour_from+' - '+hour_to if resource_calendar else 'no definido'
            data.append(values)
        return data
