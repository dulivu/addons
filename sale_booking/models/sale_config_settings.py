# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SaleConfiguration(models.TransientModel):
    _inherit = 'sale.config.settings'

    round_hours = fields.Boolean("Redondear horas a enteros",
                                           help="Al generar una reserva que no complete a una cantidad de horas "
                                                "exacta, esta se redondeará al mayor inmediato")
    round_hours_to_day = fields.Boolean("Redondear días a enteros",
                                        help="Al generar una reserva cuyas horas no completen un día (24 horas), "
                                             "y si el servicio se mide en días este será considerado "
                                             "como 1 día completo")
    no_check_in_without_partnert = fields.Boolean("Bloquear ingreso sin socio registrado",
                                                  help="Si la linea de reserva no tiene un socio registrado "
                                                       "no permitirá que esta se marqué como ingresada")

    @api.model
    def get_default_round_hours(self, fields):
        return {
            'round_hours': self.env['ir.values'].get_default('sale.config.settings', 'round_hours', False)
        }

    @api.multi
    def set_default_round_hours(self):
        ir_values = self.env['ir.values']
        ir_values.sudo()
        ir_values.set_default('sale.config.settings', 'round_hours', self.round_hours)

    @api.model
    def get_default_round_hours_to_day(self, fields):
        return {
            'round_hours_to_day': self.env['ir.values'].get_default('sale.config.settings', 'round_hours_to_day', False)
        }

    @api.multi
    def set_default_round_hours_to_day(self):
        ir_values = self.env['ir.values']
        ir_values.sudo()
        ir_values.set_default('sale.config.settings', 'round_hours_to_day', self.round_hours_to_day)

    @api.model
    def get_default_no_check_in_without_partnert(self, fields):
        return {
            'round_hours': self.env['ir.values'].get_default('sale.config.settings', 'no_check_in_without_partnert', False)
        }

    @api.multi
    def set_default_no_check_in_without_partnert(self):
        ir_values = self.env['ir.values']
        ir_values.sudo()
        ir_values.set_default('sale.config.settings', 'no_check_in_without_partnert', self.no_check_in_without_partnert)


