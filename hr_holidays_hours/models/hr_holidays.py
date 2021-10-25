# -*- coding: utf-8 -*-

from odoo import api, fields, models
import math


class HolidaysType(models.Model):

    _inherit = "hr.holidays.status"

    status_type = fields.Selection([('remove', 'Ausencia'), ('add','Recuperación')], string="Clasificación")


class Holidays(models.Model):

    _inherit = "hr.holidays"

    number_of_hours = fields.Float(string="Número de Horas", compute="_compute_hours", store=True)
    holiday_status_id = fields.Many2one(domain="['|', ('status_type', '=', type), ('status_type', '=', False)]")

    @api.depends('date_from', 'date_to', 'type')
    def _compute_hours(self):
        for holiday in self:
            if holiday.date_to:
                _from = fields.Datetime.from_string(self.date_from)
                _to = fields.Datetime.from_string(self.date_to)
                time_delta = _to - _from
                if time_delta.total_seconds() < 60*60*8:
                    holiday.number_of_hours = time_delta.total_seconds() / 3600 * (-1 if holiday.type == 'remove' else 1)
                else:
                    holiday.number_of_hours = 0.0

    def _get_number_of_days(self, date_from, date_to, employee_id):
        """ Returns a float equals to the timedelta between two dates given as string."""
        from_dt = fields.Datetime.from_string(date_from)
        to_dt = fields.Datetime.from_string(date_to)

        time_delta = to_dt - from_dt
        if time_delta.total_seconds() >= 60*60*8:
            return math.ceil(time_delta.days + float(time_delta.seconds) / 86400)
        else:
            return 0.0


