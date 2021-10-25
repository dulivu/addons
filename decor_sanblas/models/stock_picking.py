# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = "stock.picking"
    cliente_oc = fields.Char('N° O/C Cliente')
    motivo_traslado = fields.Selection([('venta', 'Venta'), ('compra', 'Compra'), ('consignacion', 'Consignación')],
                                       'Motivo de Traslado')
    transportista = fields.Many2one('res.partner', 'Transportista')
    transporte_marca = fields.Char('Marca')
    transporte_placa = fields.Char('Placa')
    transporte_licencia = fields.Char('Licencia de conducir')
