# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    nro_guia = fields.Char('Guia de Remision', compute='_compute_nro_guia')

    def _compute_nro_guia(self):
        for invoice in self:
            origin = invoice.origin
            pick = self.env['stock.picking'].search([('origin','=',origin)])
            invoice.nro_guia = pick.name
            #invoice.nro_guia=self.env['stock.picking'].search(['origin','=',invoice.origin])[0].name
