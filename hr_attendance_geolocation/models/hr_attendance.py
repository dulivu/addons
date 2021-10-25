# -*- coding: utf-8 -*-
import pytz
from odoo import models, fields, api


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    chkin_location_id = fields.Many2one('hr.geolocation', 'Ubicacion de Entrada')
    chkout_location_id = fields.Many2one('hr.geolocation', 'Ubicacion de Salida')
