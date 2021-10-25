# -*- coding: utf-8 -*-

from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = "product.template"

    qty_mesh_oven = fields.Integer("Número de mallas (horno)")
    qty_mesh_paint = fields.Integer("Número de mallas (pintura)")