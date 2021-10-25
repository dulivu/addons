# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductProduct(models.Model):
    _inherit = "product.template"

    peso = fields.Float(digits=(4, 2), string='Peso')
