# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class MrpGroupPay(models.Model):
    _inherit = 'mrp.group.pay'

    service_pay_id = fields.Many2one('product.product', string="Servicio de pago", domain=[('type', '=', 'service')], required=True)
    service_disc_id = fields.Many2one('product.product', string="Servicio de descuento", domain=[('type', '=', 'service')])
    total_qty_to_pay = fields.Integer(compute='_compute_quantities', string="Cantidad a Pagar")
    total_qty_to_disc = fields.Integer(compute='_compute_quantities', string="Cantidad a Descontar")
    can_process_pay = fields.Boolean(compute='_compute_can_process_pay')
    mesh_production_ids = fields.One2many('mesh.production', 'group_pay_id')
    observation = fields.Text()
    #paid_flag = fields.Boolean(default=False)
    state = fields.Selection(selection=[
        ('open', 'Abierto'),
        ('paid', 'Pagado')
    ], string='Estado', default='open', sotre=True)

    @api.constrains('pay_group_compute_ids')
    def _check_pay_quantities(self):
        for item in self:
            total_qty_to_pay = item.total_qty_to_pay
            total_qty_to_disc = item.total_qty_to_disc
            if total_qty_to_pay < 0 or total_qty_to_disc < 0:
                raise ValidationError('Las cantidades a pagar o descontar no deben ser negativos')
            if item.pay_group_compute_ids and sum(item.pay_group_compute_ids.mapped('workdays')) <= 0 and (
                    total_qty_to_pay or total_qty_to_disc):
                raise ValidationError('Debe establecer la cantidad de dias trabajados')

    def _compute_can_process_pay(self):
        for item in self:
            pays = item.pay_group_compute_ids.mapped('mrp_pago_ids')
            if item.total_qty_to_disc >= 0 or item.total_qty_to_pay >= 0:
                if not pays:
                    item.can_process_pay = True
                else:
                    item.can_process_pay = False
            #item.can_process_pay = item.total_qty_to_disc >= 0 or item.total_qty_to_pay >= 0 and not pays

    @api.depends('mrp_periodo_id', 'pay_group_compute_ids.individual_amount')
    def _compute_quantities(self):
        if self.env.context.get('serigraphy_pay', False):
            for groupPay in self:
                mesh_production_ids = self.env['mesh.production'].search(
                    [('production_id.mrp_periodo_id', '=', groupPay.mrp_periodo_id.id)])
                if mesh_production_ids:
                    pay_group_compute_ids = groupPay.pay_group_compute_ids
                    total_qty_to_pay = sum(mesh_production_ids.filtered(
                        lambda x: x.state_mesh == 'good' and x.state == 'open').mapped('qty')) - sum(
                        pay_group_compute_ids.filtered(lambda x: x.individual_amount > 0 and not x.mrp_pago_ids).mapped(
                            'individual_amount'))
                    total_qty_to_disc = sum(mesh_production_ids.filtered(
                        lambda x: x.state_mesh == 'bad' and x.state == 'open').mapped('qty')) + sum(
                        pay_group_compute_ids.filtered(lambda x: x.individual_amount < 0 and not x.mrp_pago_ids).mapped(
                            'individual_amount'))
                    groupPay.update({
                        'total_qty_to_pay': total_qty_to_pay,
                        'total_qty_to_disc': total_qty_to_disc,
                    })
        else:
            super(MrpGroupPay, self)._compute_quantities()

    def get_price_pay(self, discount=False):
        uom_units = self.env.ref('product.product_uom_unit')
        if not discount:
            unit_price = self.service_pay_id.uom_id._compute_price(self.service_pay_id.standard_price, uom_units)
        else:
            unit_price = self.service_disc_id.uom_id._compute_price(self.service_disc_id.standard_price, uom_units)
        return unit_price

    def process_mesh_productions(self):
        self.env['mesh.production'].search(
            [('production_id.mrp_periodo_id', '=', self.mrp_periodo_id.id)]).write({'group_pay_id': self.id})

    @api.multi
    def button_generate_pays(self):
        for groupPay in self:
            if groupPay.total_qty_to_pay < 0 or groupPay.total_qty_to_disc < 0:
                raise ValidationError('No se puede procesar cantidades negativas')
            elif groupPay.total_qty_to_pay == 0 and groupPay.total_qty_to_disc == 0:
                price_pay_unit = groupPay.get_price_pay() if groupPay.service_pay_id else False
                price_discount_unit = groupPay.get_price_pay(discount=True) if groupPay.service_disc_id else False
                groupPay.pay_group_compute_ids.generate_pays(groupPay.service_pay_id, price_pay_unit,
                                                             groupPay.total_qty_to_pay)
                groupPay.pay_group_compute_ids.generate_pays(groupPay.service_disc_id, price_discount_unit,
                                                             groupPay.total_qty_to_disc)
                groupPay.process_mesh_productions()
                #groupPay.paid_flag = True
                groupPay.state = 'paid'
            else:
                raise ValidationError('No se puede procesar porque aun existen cantidades a pagar o a descontar')

    @api.multi
    def button_revert_pays(self):
        for item in self:
            if item.mrp_periodo_id.active:
                item.pay_group_compute_ids.mapped('mrp_pago_ids').unlink()
                item.mesh_production_ids.write({'group_pay_id': None})
            #item.paid_flag = False
            item.state = 'open'
