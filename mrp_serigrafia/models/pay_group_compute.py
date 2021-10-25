# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PayGroupCompute(models.Model):
    _inherit = "pay.group.compute"

    individual_amount = fields.Integer("Cantidad Individual")

    def generate_pays(self, service_id, price, qty):
        MrpPago = self.env['mrp.pago']
        for item in self:
            if item.individual_amount > 0 and price > 0:
                amount = item.individual_amount * price
                MrpPago.create(item.format_values(service_id, item.individual_amount, amount))
            if item.individual_amount < 0 and price < 0:
                amount = abs(item.individual_amount) * price
                MrpPago.create(item.format_values(service_id, abs(item.individual_amount), amount))
            if item.workdays and qty:
                amount = (item.percentage / 100) * (price * qty)
                MrpPago.create(item.format_values(service_id, qty, amount))

    def format_values(self, service_id, qty, amount):
        return {
            'servicio_id': service_id.id,
            'price': service_id.standard_price,
            'empleado_id': self.employee_id.id,
            'qty': qty,
            'monto': amount,
            'fecha_pago': fields.Date.today(),
            'pay_group_compute_id': self.id
        }

    @api.multi
    def write(self, values):
        for item in self:
            if item.mrp_pago_ids:
                raise ValidationError('El registro ya tiene pagos generados')
            else:
                super(PayGroupCompute, self).write(values)