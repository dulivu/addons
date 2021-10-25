# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, exceptions

class SaleOrderStage(models.Model):
	_name = 'sale.order.stage'
	_description = 'Stage of sale order'
	_order = 'sequence'

	name = fields.Char('Nombre', translate=True, required=True)
	sequence = fields.Integer('Secuencia', help='Usado para organizar pedidos de venta', default=1)
	team_id = fields.Many2one('crm.team', string='Equipo', ondelete='set null', help='Equipo especifico que usa esta etapa. Otros equipos no serán capaces de ver o usar esta etapa.')
