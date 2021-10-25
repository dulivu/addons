# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PickingType(models.Model):
    _inherit = "stock.picking.type"
    generar_factura = fields.Boolean("Generar Factura", help="Si está activo el movimiento generara una factura")
