# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    mesh_ids = fields.One2many("mesh.production", "production_id", string="Mallas")
    total_qty_mesh = fields.Integer(string="Total de mallas", compute="_compute_total_mesh")
    qty_good_mesh = fields.Integer(string="Mallas Buenas", compute="compute_qty_mesh")
    qty_bad_mesh = fields.Integer(string="Mallas Malas", compute="compute_qty_mesh")

    @api.multi
    def _compute_total_mesh(self):
        for production in self:
            product_id = production.product_id
            production.total_qty_mesh = product_id.qty_mesh_oven + product_id.qty_mesh_paint

    @api.constrains('mesh_ids')
    def check_mesh_ids(self):
        for production in self: mesh_ids = production.mesh_ids
        if mesh_ids:
            production_qty_mesh = production.total_qty_mesh
            total_qty_mesh = sum(mesh_ids.mapped('qty'))
            if total_qty_mesh != production_qty_mesh:
                raise ValidationError(
                    'El total de mallas registradas debe ser igual al total de mallas disponibles')

    def compute_qty_mesh(self):
        for production in self:
            mesh_ids = production.mesh_ids
            production.qty_good_mesh = sum(mesh_ids.filtered(lambda x: x.state_mesh == 'good').mapped('qty'))
            production.qty_bad_mesh = sum(mesh_ids.filtered(lambda x: x.state_mesh == 'bad').mapped('qty'))
