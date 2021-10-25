# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, exceptions
import datetime
import pytz
import math


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    booking_ids = fields.One2many('sale.order.booking', 'order_id')
    partner_ids = fields.Many2many('res.partner', string='Socios', copy=False)

    @api.multi
    def action_done(self):
        for booking in self.booking_ids:
            booking.write({'state_booking': 'checked_out'})
        return super(SaleOrder, self).action_done()


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    @api.depends('booking_id.check_in', 'booking_id.check_out')
    def _compute_qty(self):
        for line in self:
            if line.booking_id:
                hours = line.booking_id.get_interval()
                line.set_time_qty(hours[0])
            else:
                return 1

    booking_id = fields.One2many('sale.order.booking', 'order_line')
    product_uom_qty = fields.Float(default=_compute_qty, store=True, readonly=False)

    @api.one
    def set_time_qty(self, hours):
        if self.product_id and hours:
            day = self.env.ref('product.product_uom_day')
            hour = self.env.ref('product.product_uom_hour')
            unit = self.env.ref('product.product_uom_unit')

            if self.product_id.uom_id.id == hour.id:
                round_hours = self.env['ir.values'].get_default('sale.config.settings', 'round_hours')
                self.product_uom_qty = math.ceil(hours) if round_hours else hours
            elif self.product_id.uom_id.id == day.id:
                round_hours_to_day = self.env['ir.values'].get_default('sale.config.settings', 'round_hours_to_day')
                self.product_uom_qty = math.ceil(hours / 24) if round_hours_to_day else hours / 24
            elif self.product_id.uom_id.id != unit.id:
                self.product_uom_qty = day._compute_quantity(hours / 24, self.product_id.uom_id)
            else:
                self.product_uom_qty = self.product_uom_qty if self.product_uom_qty else 1


class SaleOrderBooking(models.Model):
    _name = 'sale.order.booking'
    _inherits = {'sale.order.line': 'order_line'}
    _inherit = ['mail.thread']
    _description = 'Reservas'
    _order = 'check_in'

    def _default_check_in(self):
        now = datetime.datetime.utcnow()
        now = fields.Datetime.context_timestamp(self, now)
        now = now.replace(hour=12, minute=0, second=0)
        return now.astimezone(pytz.utc)

    def _default_check_out(self):
        now = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        now = fields.Datetime.context_timestamp(self, now)
        now = now.replace(hour=12, minute=0, second=0)
        return now.astimezone(pytz.utc)

    order_line = fields.Many2one('sale.order.line', required=True, ondelete='cascade')
    check_in = fields.Datetime('Inicio', index=True, required=True, default=_default_check_in)
    check_out = fields.Datetime('Fin', index=True, required=True, default=_default_check_out)
    state_booking = fields.Selection([
        ('booked', 'Reservado'),
        ('checked_in', 'Entró'),
        ('checked_out', 'Salió'),
    ], string='Estado', default='booked', copy=False, required=True)

    @api.multi
    def unlink(self):
        for line in self:
            line.order_line.unlink()

    @api.one
    def get_interval(self):
        if self.check_in and self.check_out:
            # se estima que el mínimo, sea horas
            dif = fields.Datetime.from_string(self.check_out) - fields.Datetime.from_string(self.check_in)
            return dif.total_seconds() / 3600
        else:
            return 0

    @api.multi
    @api.onchange('order_id')
    def order_id_change(self):
        self.product_id_change()

    @api.constrains('check_in', 'check_out')
    def _check_validity_check_in_check_out(self):
        """ verifies if check_in is earlier than check_out. """
        for line in self:
            if line.check_in and line.check_out:
                if line.check_out < line.check_in:
                    raise exceptions.ValidationError(_('La fecha de ingreso no puede ser posterior a la fecha de salida'))

    # TODO: desde la vista calendario no permite modificar la fecha final, porque simula la modificación del ingreso también
    @api.multi
    @api.constrains('check_in')
    def _check_in(self):
        for line in self:
            if line.state_booking != 'booked':
                raise exceptions.ValidationError('No puede modificar la fecha de ingreso de una reserva que ya ingresó, si quiere actualizar su fecha de salida intentelo por la orden de venta')

    @api.multi
    @api.constrains('check_out')
    def _check_out(self):
        for line in self:
            if line.state_booking == 'checked_out':
                raise exceptions.ValidationError('No se puede modificar un reserva concluída')

    @api.multi
    def do_check_in(self):
        for line in self:
            if line.order_id.state in ['draft', 'cancel', 'sent']:
                raise exceptions.ValidationError("La orden está cancelada ó aún no ha sido confirmada")
            elif line.state_booking == 'checked_out':
                raise exceptions.ValidationError("La reserva ya fue marcada como finalizada")
            else:
                if self.env['ir.values'].get_default('sale.config.settings', 'no_check_in_without_partnert'):
                    if not line.partner_ids:
                        raise exceptions.ValidationError("Se requiere registre al menos un socio en la reserva")
                line.state_booking = 'checked_in'

    @api.multi
    def do_check_out(self):
        for line in self:
            if line.order_id.state in ['draft', 'cancel', 'sent']:
                raise exceptions.ValidationError("La orden está cancelada ó aún no ha sido confirmada")
            elif line.state_booking == 'booked':
                raise exceptions.ValidationError("La reserva aún no fue marcada como 'ingresada'")
            else:
                line.state_booking = 'checked_out'

    @api.multi
    def do_return(self):
        for line in self:
            if line.state_booking == 'checked_out':
                line.state_booking = 'checked_in'
            elif line.state_booking == 'checked_in':
                line.state_booking = 'booked'

    ###################################################
    # Code from sale.order.line, needed for interaction
    ###################################################

    @api.multi
    def _get_display_price(self, product):
        # TO DO: move me in master/saas-16 on sale.order
        if self.order_id.pricelist_id.discount_policy == 'with_discount':
            return product.with_context(pricelist=self.order_id.pricelist_id.id).price
        product_context = dict(self.env.context, partner_id=self.order_id.partner_id.id, date=self.order_id.date_order,
                               uom=self.product_uom.id)
        final_price, rule_id = self.order_id.pricelist_id.with_context(product_context).get_product_price_rule(
            self.product_id, self.product_uom_qty or 1.0, self.order_id.partner_id)
        base_price, currency_id = self.with_context(product_context)._get_real_price_currency(product, rule_id,
                                                                                              self.product_uom_qty,
                                                                                              self.product_uom,
                                                                                              self.order_id.pricelist_id.id)
        if currency_id != self.order_id.pricelist_id.currency_id.id:
            base_price = self.env['res.currency'].browse(currency_id).with_context(product_context).compute(base_price,
                                                                                                            self.order_id.pricelist_id.currency_id)
        # negative discounts (= surcharge) are included in the display price
        return max(base_price, final_price)

    @api.multi
    def _compute_tax_id(self):
        for line in self:
            fpos = line.order_id.fiscal_position_id or line.order_id.partner_id.property_account_position_id
            # If company_id is set, always filter taxes by the company
            taxes = line.product_id.taxes_id.filtered(lambda r: not line.company_id or r.company_id == line.company_id)
            line.tax_id = fpos.map_tax(taxes, line.product_id, line.order_id.partner_shipping_id) if fpos else taxes

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return {'domain': {'product_uom': []}}

        vals = {}
        domain = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            vals['product_uom'] = self.product_id.uom_id
            vals['product_uom_qty'] = 1.0

        product = self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id.id,
            quantity=vals.get('product_uom_qty') or self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id
        )

        result = {'domain': domain}

        title = False
        message = False
        warning = {}
        if product.sale_line_warn != 'no-message':
            title = _("Warning for %s") % product.name
            message = product.sale_line_warn_msg
            warning['title'] = title
            warning['message'] = message
            result = {'warning': warning}
            if product.sale_line_warn == 'block':
                self.product_id = False
                return result

        name = product.name_get()[0][1]
        if product.description_sale:
            name += '\n' + product.description_sale
        vals['name'] = name

        self._compute_tax_id()

        if self.order_id.pricelist_id and self.order_id.partner_id:
            vals['price_unit'] = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)
        self.update(vals)
        return result

    @api.onchange('product_id', 'price_unit', 'product_uom', 'product_uom_qty', 'tax_id')
    def _onchange_discount(self):
        if not (self.product_id and self.product_uom and
                self.order_id.partner_id and self.order_id.pricelist_id and
                self.order_id.pricelist_id.discount_policy == 'without_discount' and
                self.env.user.has_group('sale.group_discount_per_so_line')):
            return

        self.discount = 0.0
        product = self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id.id,
            quantity=self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id,
            fiscal_position=self.env.context.get('fiscal_position')
        )

        product_context = dict(self.env.context, partner_id=self.order_id.partner_id.id, date=self.order_id.date_order, uom=self.product_uom.id)

        price, rule_id = self.order_id.pricelist_id.with_context(product_context).get_product_price_rule(self.product_id, self.product_uom_qty or 1.0, self.order_id.partner_id)
        new_list_price, currency_id = self.with_context(product_context)._get_real_price_currency(product, rule_id, self.product_uom_qty, self.product_uom, self.order_id.pricelist_id.id)

        if new_list_price != 0:
            if self.order_id.pricelist_id.currency_id.id != currency_id:
                # we need new_list_price in the same currency as price, which is in the SO's pricelist's currency
                new_list_price = self.env['res.currency'].browse(currency_id).with_context(product_context).compute(new_list_price, self.order_id.pricelist_id.currency_id)
            discount = (new_list_price - price) / new_list_price * 100
            if discount > 0:
                self.discount = discount
