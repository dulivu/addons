# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, exceptions

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _get_statements(self):
        self.statements_count = len(self.statement_ids)

    statement_ids = fields.One2many('account.bank.statement', 'sale_order_id', string="Declaraciones")
    statements_count = fields.Integer(string='Declaraciones', compute='_get_statements', readonly=True)