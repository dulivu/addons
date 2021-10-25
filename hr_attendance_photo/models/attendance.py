# -*- coding: utf-8 -*-

from odoo import models, fields

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    photo_in = fields.Binary("Foto ingreso", attachment=True)
    photo_out = fields.Binary("Foto salida", attachment=True)
