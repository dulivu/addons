# -*- coding: utf-8 -*-

from odoo import models, fields, api

class HrGeolocation(models.Model):
    _name = 'hr.geolocation'

    name = fields.Char('Ubicacion')
    latitude = fields.Char('Latitud')
    longitude = fields.Char('Longitud')
    photo = fields.Binary("Foto", attachment=True)