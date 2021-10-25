# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, exceptions


class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'

    sale_order_id = fields.Many2one('sale.order', string='Pedido de venta', index=True, copy=False, ondelete='set default')


class AccountBankStatementLine(models.Model):
	_inherit = 'account.bank.statement.line'

	@api.model
	def _default_partner_id(self):
		print self.statement_id
		if self.statement_id.sale_order_id:
			return self.statement_id.sale_order_id.partner_id

	partner_id = fields.Many2one(default=_default_partner_id, store=True)
