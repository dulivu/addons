# -*- coding: utf-8 -*-
from odoo import fields, models, api
import pytz
from datetime import datetime

class UpdateAttendance(models.TransientModel):
    _name='hr.attendance.update.wizard'
    _description='Actualizacion de asistencias de un empleado'

    employee_id = fields.Many2one('hr.employee')
    date_from = fields.Date('Fecha Desde')
    date_to = fields.Date('Fecha Hasta')

    def button_update_attendances(self):
        zone = pytz.timezone(self._context.get('tz') or self.env.user.tz)
        lc_date_from = zone.localize(datetime.combine(fields.Date.from_string(self.date_from),datetime.min.time()))
        lc_date_to = zone.localize(datetime.combine(fields.Date.from_string(self.date_to),datetime.max.time()))
        attendances = self.env['hr.attendance'].search([
            ('employee_id','=',self.employee_id.id),
            ('check_in','>=',fields.Datetime.to_string(lc_date_from.astimezone(pytz.utc))),
            ('check_in','<=',fields.Datetime.to_string(lc_date_to.astimezone(pytz.utc)))])
        attendances._compute_worked_hours()