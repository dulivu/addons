# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import datetime
from datetime import datetime, date, time

class MrpDescuentos(models.Model):
    _name = "mrp.descuento"
    _rec_name = "sequence_id"


    concepto = fields.Char('Concepto', required=True)
    pago_ids = fields.One2many('mrp.pago', 'descuento_ids', 'Descuento')
    cost = fields.Float('Costo', required=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.user.company_id.currency_id)
    sequence_id = fields.Char(string="Recibo", copy=False, readonly=True,
                           index=True, default=lambda self: _('New'))
    amount_total = fields.Float('Total', store=True)
    empleado_ids = fields.Many2many('hr.employee', string='Empleado')
    fecha = fields.Date('Fecha', required=True)
    observacion = fields.Text('Observaciones')
    paid_flag = fields.Boolean(default=False)
    period_aux = fields.Date('Periodo aux', default=fields.Date.today)
    period = fields.Char('Periodo', compute='date_period', store=True)
    periodo = fields.Many2one('mrp.periodo', string='Periodo')
    state = fields.Selection([
        ('draft', 'Nuevo'),
        ('done', 'Realizado'),
        ('paid', 'Pagado')
    ], string="Estado", default="draft")

    @api.depends('period_aux')
    def date_period(self):
        for i in self:
            if i.period_aux:
                month = datetime.strptime(str(i.period_aux), '%Y-%m-%d').strftime('%m')
                year = datetime.strptime(str(i.period_aux), '%Y-%m-%d').strftime('%Y')
                i.period = month + '/' + year

    @api.model
    def create(self, vals):
        if vals.get('sequence_id', _('New')) == _('New'):
            vals['sequence_id'] = self.env['ir.sequence'].next_by_code('mrp.descuento') or _('New')
        res = super(MrpDescuentos, self).create(vals)
        return res

    @api.constrains('cost')
    def validate_cost(self):
        for i in self:
            if i.cost >= 0:
                raise ValidationError('El pago debe ser negativo')

    @api.multi
    def button_descontar(self):
        if self.empleado_ids:
            self.ensure_one()
            pagos = []
            for e in self.empleado_ids.ids:
                vals = {
                    'descuento_ids': self.id,
                    'concept': self.concepto,
                    'empleado_id': e,
                    'fecha_pago': self.fecha
                }
                pagos.append(vals)
            pago = self.env['mrp.pago']
            #monto = self._monto_aux(self.servicio_id)
            monto = self.cost / len(pagos)
            for p in pagos:
                p['monto'] = monto
                pago.create(p)
            self.empleado_ids = None
        else:
            raise ValidationError('Debe asignar al menos un empleado')

    def button_mark_done(self):
        self.state = 'done'
        self.validate_discount()

    def button_generate_discount(self):
        self.paid_flag = True
        self.state = 'paid'
        self.validate_discount()

    def validate_discount(self):
        for i in self:
            if not i.pago_ids:
                raise ValidationError('No existen registros de descuento')

    @api.multi
    def button_anular_descuento(self):
        for i in self:
            i.state = 'done'
            i.paid_flag = False
            if i.pago_ids:
                i.pago_ids.filtered(lambda x: x.monto < 0).unlink()
            elif not i.pago_ids:
                raise ValidationError('No existen registros de descuento a eliminar')

    def generate_pays(self):
        self.button_generate_discount()

