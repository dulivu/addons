# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import datetime
from datetime import datetime

class MrpBonus(models.Model):
    _name = 'mrp.bonus'
    _rec_name = 'concepto'

    type = fields.Selection([
        ('bonus', 'Bono'),
        ('fixed_salary', 'Sueldo Fijo')], string='Tipo', required=True)
    concepto = fields.Char('Concepto', required=True)
    pago_ids = fields.One2many('mrp.pago', 'bono_ids', 'Bono')
    cost = fields.Float('Monto', required=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.user.company_id.currency_id)
    #sequence_id = fields.Char()
    employee_ids = fields.Many2many('hr.employee', string='Empleado')
    periodo = fields.Many2one('mrp.periodo', string='Periodo')
    fecha = fields.Date('Fecha')
    observacion = fields.Text('Observaciones')
    paid_flag = fields.Boolean(default=False)
    period = fields.Char('Periodo', compute='date_period', store=True)
    period_aux = fields.Date(default=fields.Date.today())
    state = fields.Selection([
        ('draft', 'Nuevo'),
        ('done', 'Realizado'),
        ('paid', 'Pagado')
    ], string='Estado', default='draft')

    @api.depends('period_aux')
    def date_period(self):
        if self.period_aux:
            month = datetime.strptime(str(self.period_aux), '%Y-%m-%d').strftime('%m')
            year = datetime.strptime(str(self.period_aux), '%Y-%m-%d').strftime('%Y')
            self.period = month + year

    @api.constrains('cost')
    def validate_cost(self):
        for i in self:
            if i.cost <= 0:
                raise ValidationError('El pago debe ser mayor a 0')

    @api.multi
    def button_bonus(self):
        if self.employee_ids:
            self.ensure_one()
            pagos = []
            for e in self.employee_ids.ids:
                vals = {
                    'bono_ids': self.id,
                    'concept': self.concepto,
                    'empleado_id': e,
                    'fecha_pago': self.fecha
                }
                pagos.append(vals)
            pago = self.env['mrp.pago']
            monto = self.cost / len(pagos)
            if monto <= 0:
                raise ValidationError('Pago menor o igual a 0')
            else:
                for p in pagos:
                    p['monto'] = monto
                    pago.create(p)
            self.employee_ids = None
        else:
            raise ValidationError('Debe asignar al menos un empleado')

    @api.one
    def button_mark_done(self):
        self.validate_type()
        self.validate_bonus()
        self.write({'state': 'done'})

    @api.one
    def button_generate_bonus(self):
        self.paid_flag = True
        self.validate_type()
        self.validate_bonus()
        self.write({'state': 'paid'})

    def validate_bonus(self):
        if not self.pago_ids:
            raise ValidationError('No existen registros de bonos')

    def validate_type(self):
        if not self.type:
            raise ValidationError('Debe asignar el tipo')

    @api.multi
    def button_cancel_bonus(self):
        for i in self:
            i.write({'state': 'done'})
            if i.pago_ids:
                i.pago_ids.filtered(lambda x: x.monto > 0).unlink()
            else:
                raise ValidationError('No existen registros de pago')

    @api.one
    def generate_bonus(self):
        self.button_generate_bonus()

