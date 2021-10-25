# -*- coding: utf-8 -*-

from odoo import fields, models, api, _, exceptions


class ICM (models.Model):
    _name = "covid.imc"

    user_id = fields.Many2one('res.users', 'Usuario')
    date = fields.Date('Fecha')
    weight = fields.Float('Peso (kgs)', digits=(16, 2))
    height = fields.Float('Altura (mtrs)', digits=(16, 2))
    imc = fields.Float('IMC', digits=(16, 2), compute='_compute_imc')

    @api.depends('height', 'weight')
    @api.multi
    def _compute_imc(self):
        for imc in self:
            imc.imc = imc.weight/(imc.height*imc.height)
            if imc.imc > 30:
                employee = self.env['hr.employee'].search([('user_id', '=', imc.user_id.id)])
                employee.write({'covid_enabled': True})
