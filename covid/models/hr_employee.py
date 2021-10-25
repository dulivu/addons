# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Employee(models.Model):
    _inherit = 'hr.employee'

    covid_enabled = fields.Boolean('Inhabilitado')

    @api.multi
    def covid_e(self):
        for line in self:
            line.covid_enabled = True

    @api.multi
    def covid_d(self):
        for line in self:
            line.covid_enabled = False
