# -*- coding: utf-8 -*-
import googlemaps
from odoo import models, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.multi
    def update_attendances(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.attendance.update.wizard',  # this model
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_employee_id': self.id}
        }
