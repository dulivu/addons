# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from collections import defaultdict
from odoo.exceptions import ValidationError
import datetime
from datetime import datetime


class MrpAdicionales(models.Model):
    _name = "mrp.adicional"
    _description = "Modelo que permite el ingreso de pagos adicionales"
    _rec_name = "sequence_id"

    @api.depends('date_start', 'date_end')
    def _compute_duration_time(self):
        for adicional in self:
            if adicional.date_start and self.date_end:
                time_diff = fields.Datetime.from_string(adicional.date_end) - fields.Datetime.from_string(
                    adicional.date_start)
                adicional.duration_time = round((time_diff.total_seconds() / 60.0) / 60.0, 2)
                #adicional.duration_time = repr(round(round(time_diff.total_seconds() / 60.0, 2)/60.0, 2)) + " Horas"

    @api.onchange('area_id')
    def _cargar_servicio(self):
        for i in self:
            if i.area_id.id == 22:
                return {
                    'domain': {'servicio_id': [('categ_id.name', 'ilike', 'carros')]}
                }
            if i.area_id.id == 23:
                return {
                    'domain': {'servicio_id': [('categ_id.name', 'ilike', 'pintura')]}
                }
            if i.area_id.id == 24:
                return {
                    'domain': {'servicio_id': [('categ_id.name', 'ilike', 'horno')]}
                }
            if i.area_id.id == 25:
                return {
                    'domain': {'servicio_id': [('categ_id.name', 'ilike', 'corte')]}
                }
            if i.area_id.id == 27:
                return {
                    'domain': {'servicio_id': ['|', ('categ_id.name', 'ilike', 'encajado'),
                                               ('categ_id.name', 'ilike', 'termoencogido')]}
                }
            if i.area_id.id == 39:
                return {
                    'domain': {'servicio_id': [('categ_id.name', 'ilike', 'pintado zocalos')]}
                }
            if i.area_id.id == 40:
                return {
                    'domain': {'servicio_id': ['|', ('categ_id.name', 'ilike', 'serigrafia'),
                                               ('categ_id.name', 'ilike', 'armado mallas')]}
                }
            if i.area_id.id == 41:
                return {
                    'domain': {'servicio_id': [('categ_id.name', 'ilike', 'vidrio')]}
                }
            if i.area_id.id == 31:
                return {
                    'domain': {'servicio_id': [('categ_id.name', 'ilike', 'pintura vidrio')]}
                }
            if i.area_id.id == 43:
                return {
                    'domain': {'servicio_id': [('categ_id.name', 'ilike', 'mantenimiento')]}
                }

    @api.onchange('servicio_id')
    def _type_pay(self):
        for i in self:
            if i.servicio_id.uom_id.id == 5:
                i.type_pay = True
            else:
                i.type_pay = False

    sequence_id = fields.Char(string='Recibo', copy=False, readonly=True,
                              required=True, index=True, default=lambda self: _('New'))
    servicio_id = fields.Many2one('product.product', 'Servicio', domain=[('type', '=', 'service')])
    pago_ids = fields.One2many('mrp.pago', 'adicionales_ids', 'Pagos')
    description = fields.Char('Descripción')
    qty = fields.Float('Cantidad (Unidades)', required=True)
    #product_uom_id = fields.Many2one('product.uom', 'Unidad de medida')
    date_start = fields.Datetime('Fecha Inicio')
    date_end = fields.Datetime('Fecha Fin')
    duration_time = fields.Float(compute="_compute_duration_time", store=True, string="Duracion de Tiempo")
    work_date = fields.Date('Fecha del trabajo', required=True)
    workcenter_id = fields.Many2one('mrp.workcenter', 'Centro de Trabajo')
    area_id = fields.Many2one('mrp.workcenter', 'Area')
    empleado_ids = fields.Many2many('hr.employee', string="Empleados")
    manual_option = fields.Boolean(string="Opciones Manuales", default=False)
    type_pay = fields.Boolean(string="Pago por tiempo", default=False)
    manual_time = fields.Boolean(string="Tiempo Manual", default=False)
    cost = fields.Float(string="Costo (Millar)", required=True, store=True)
    amount_total = fields.Monetary(string="Total", compute="_calculate_pay", store=True)
    currency_id = fields.Many2one("res.currency", default=lambda self: self.env.user.company_id.currency_id)
    observacion = fields.Text('Observaciones')
    periodo = fields.Many2one('mrp.periodo', string='Periodo')
    #aux
    inicio_aux = fields.Float('Inicio')
    fin_aux = fields.Float('Fin')
    duration_aux = fields.Float(string='Duracion', compute='_compute_aux_duration_time', store=True, readonly=False)
    #cost_aux = fields.Float(string='costo', default=5)
    total_aux = fields.Float(string='Total', compute='_compute_aux_total')
    paid_flag = fields.Boolean(default=False)
    period_aux = fields.Date(default=fields.Date.today)
    period = fields.Char(store=True, compute='date_period')
    state = fields.Selection([
        ('draft', 'Nuevo'),
        ('done', 'Realizado'),
        #('validated', 'Validado'),
        ('paid', 'Pagado')
    ], string="Estado", default="draft")

    @api.depends('period_aux')
    def date_period(self):
        for i in self:
            if i.period_aux:
                month = datetime.strptime(str(i.period_aux), '%Y-%m-%d').strftime('%m')
                year = datetime.strptime(str(i.period_aux), '%Y-%m-%d').strftime('%Y')
                i.period = month + '/' + year

    @api.depends('cost', 'duration_aux')
    def _compute_aux_total(self):
        for i in self:
            i.total_aux = i.cost * i.duration_aux

    @api.depends('inicio_aux', 'fin_aux')
    def _compute_aux_duration_time(self):
        for i in self:
            if i.inicio_aux and i.fin_aux:
                d = i.fin_aux - i.inicio_aux
                i.duration_aux = d

    @api.depends('cost', 'qty', 'duration_aux')
    def _calculate_pay(self):
        for i in self:
            if i.type_pay == False:
                amount = (i.cost)/1000 * i.qty
                i.amount_total = amount
            if i.type_pay == True:
                t = i.duration_aux
                i.amount_total = i.cost * t

    @api.onchange('servicio_id')
    def _cargar_costo(self):
        for i in self:
            i.cost = i.servicio_id.standard_price

    # @api.one
    # @api.constrains('pay')
    # def _check_amount(self):
    #     if not self.pay > 0.0:
    #         raise ValueError('El pago debe ser mayor a cero')

    @api.model
    def create(self, values):
        if values.get('sequence_id', _('New')) == _('New'):
            values['sequence_id'] = self.env['ir.sequence'].next_by_code('mrp.adicional') or _('New')
        res = super(MrpAdicionales, self).create(values)
        return res

    # @api.one
    # @api.depends('servicio_id')
    # def _compute_product_uom(self):
    #     self.product_uom_id = self.servicio_id.uom_id

    #@api.multi
    def button_llenar_personal(self):
        self.ensure_one()
        #if self.workcenter_id:
        employee_ids = self.workcenter_id.employee_ids.ids
        a = ','.join([str(i) for i in employee_ids])
        #query = "SELECT employee_id FROM hr_attendance where check_in::DATE = '%s' and employee_id in (%s)" % (str(self.work_date), a)
        query = "SELECT ID FROM hr_employee where id in (%s)" % (a)
        cr = self.env.cr
        cr.execute(query)
        data = cr.fetchall()
        ids = [x[0] for x in data]
        self.empleado_ids = [(6, 0, ids)]
        return {
            "type": "ir.actions.do_nothing",
        }

    def _monto_aux(self, servicio_id, qty, pagos):
        if self.type_pay == False:
            monto = ((servicio_id.standard_price)/1000 * qty) / pagos
            return monto
        if self.type_pay == True:
            monto = (self.duration_aux * servicio_id.standard_price) / pagos
            return monto

    @api.multi
    def button_adicionar(self):
        if self.empleado_ids:
            self.ensure_one()
            pagos = []
            for e in self.empleado_ids.ids:
                vals = {
                    'adicionales_ids': self.id,
                    'servicio_id': self.servicio_id.id,
                    'empleado_id': e,
                    'qty': self.qty,
                    'fecha_pago': self.work_date
                }
                pagos.append(vals)
            pago = self.env['mrp.pago']
            #monto = pago._calcular_monto(self.servicio_id, len(pagos), self.qty)
            monto = self._monto_aux(self.servicio_id, self.qty, len(pagos))
            for p in pagos:
                p['monto'] = monto
                pago.create(p)
            self.empleado_ids = None
            self.area_id = None
            self.servicio_id = None
            self.qty = 0
            self.cost = 0
            self.amount_total = 0
            self.inicio_aux = 0.0
            self.fin_aux = 0.0
            self.duration_aux = 0.0
        else:
            raise ValidationError('Debe asignar al menos un empleado')

    def button_mark_done(self):
        self.state = 'done'
        self.validate_pago()

    def button_generate_payments(self):
        self.paid_flag = True
        self.state = 'paid'
        self.validate_pago()

    @api.multi
    def write(self, vals):
        wos = super(MrpAdicionales, self).write(vals)
        self.env['bus.bus'].sendone('auto_refresh', 'mrp.adicional')
        return wos

    def generate_pays(self):
        self.button_generate_payments()

    def validate_pago(self):
        for i in self:
            if not i.pago_ids:
                raise ValidationError('No existen registros de pago')

    @api.multi
    def button_anular_payment(self):
        for i in self:
            i.state = 'done'
            i.paid_flag = False
            if i.pago_ids:
                i.pago_ids.filtered(lambda x: x.monto > 0).unlink()
            elif not i.pago_ids:
                raise ValidationError('No existen registros de pago a eliminar')

class MrpPago(models.Model):
    _inherit = 'mrp.pago'

    adicionales_ids = fields.Many2one('mrp.adicional', 'Adicionales', ondelete='cascade')
    descuento_ids = fields.Many2one('mrp.descuento', 'Descuento', ondelete='cascade')
    bono_ids = fields.Many2one('mrp.bonus', 'Bono', ondelete='cascade')
    concept = fields.Char('Concepto')





    # @api.multi
    # def _crear_mrp_pago(self, empleado_ids, servicio_id):
    #     pago = self.env['mrp.pago']
    #     values = {
    #         'servicio_id': servicio_id.id,
    #         'workorder_id': self.id
    #     }
    #     for empleado in empleado_ids:
    #         values['empleado_id'] = empleado.id
    #         pago.create(values)

    # def _crear_datos_pago(self, empleados, qty, servicio_id, work_date, adicionales=False):
    #     pago = self.env['mrp.pago']
    #     adicional_id = []
    #     values = {
    #         'servicio_id': servicio_id,
    #         'adicionales_ids': adicionales,
    #         'qty': qty,
    #         'fecha_pago': work_date
    #     }
    #     for e in empleados:
    #         values['empleado_id'] = e.id
    #         adicional_id.append(pago.create(values))
    #     return adicional_id
