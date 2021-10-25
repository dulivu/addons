# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class MeshProduction(models.Model):
    _name = "mesh.production"

    name = fields.Char('Referencia')
    production_id = fields.Many2one('mrp.production', string='Ficha de producción')
    state_mesh = fields.Selection(selection=[
        ('good', 'Bueno'),
        # ('regular', 'Regular'),
        ('bad', 'Malo')
    ], string="Estado de malla", default='good', states={'paid': [('readonly', True)]})
    delivery_time = fields.Selection(selection=[
        ('UDA', 'Un día antes'),
        ('ED', 'En el dia'),
        ('CR', 'Con retraso')
    ], string="Tiempo", default='UDA', states={'paid': [('readonly', True)]})
    qty = fields.Integer('Cantidad', default=1, states={'paid': [('readonly', True)]})
    state = fields.Selection(selection=[
        ('open', 'Abierto'),
        ('paid', 'Pagado')
    ], string="Estado", default='open', compute="_compute_state", store=True)
    group_pay_id = fields.Many2one('mrp.group.pay', string="Grupo de pago")

    @api.depends('group_pay_id')
    def _compute_state(self):
        for item in self:
            if item.group_pay_id:
                item.state = 'paid'
            else:
                item.state = 'open'

    @api.multi
    def write(self, values):
        for item in self:
            group_pay_id = values.get('group_pay_id', False)
            if group_pay_id is not None and not group_pay_id and item.state == 'paid' and item.group_pay_id:
                raise ValidationError('No se puede modificar el registro de malla pagada')
            else:
                super(MeshProduction, self).write(values)

    @api.multi
    def unlink(self):
        for item in self:
            if item.state == 'paid' and item.group_pay_id:
                raise ValidationError('No se puede eliminar el registro de malla pagada')
            else:
                super(MeshProduction, self).unlink()


class CustomReport(models.AbstractModel):
    _name = 'report.mrp_serigrafia.report_mesh_production'

    @api.model
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('mrp_serigrafia.report_mesh_production')
        # mesh_production_ids = self.env['mesh.production'].read_group([('production_id.mrp_periodo_id', 'in', docids)],
        #                                                              ['production_id', 'qty'], ['production_id'],
        #                                                              lazy=False)
        mrp_production_ids = self.env['mrp.production'].search([('mrp_periodo_id', 'in', docids)]).filtered(
            lambda x: x.mesh_ids)
        docargs = {
            'doc_ids': mrp_production_ids.ids,
            'doc_model': report.model,
            'docs': mrp_production_ids,
        }
        return report_obj.render('mrp_serigrafia.report_mesh_production', docargs)
