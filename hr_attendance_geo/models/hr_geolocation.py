# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrGeolocation(models.Model):
    _name = 'hr.geolocation'

    name = fields.Char('Location name')
    latitude = fields.Char('Latitude')
    longitude = fields.Char('Longitude')