# -*- coding: utf-8 -*-

from odoo import fields, models


class Temp (models.Model):
    _name = "covid.temp"

    user_id = fields.Many2one('res.users', 'Usuario')
    datetime = fields.Datetime('Fecha')
    temp = fields.Float('Temperatura', digits=(16, 2))
