# -*- coding: utf-8 -*-

from odoo import models, api, fields, SUPERUSER_ID, _
import googlemaps

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.multi
    def attendance_manual(self, next_action, entered_pin=None, latitude=None, longitude=None):
        self.ensure_one()
        action_message = super(HrEmployee, self).attendance_manual(next_action, entered_pin)
        attendance = self.env['hr.attendance'].browse(action_message['action']['attendance']['id'])
        if (latitude is not None) and (longitude is not None):
            gmaps = googlemaps.Client(key='AIzaSyCUCK6kK0PFUk37eTaRpuhawzZdJbr3lYs')
            check = self._create_hr_geolocation(
                gmaps.reverse_geocode((float(latitude), float(longitude)))[0]['formatted_address'],
                latitude, longitude)
        else:
            check = self._create_hr_geolocation('Desconocido', '', '')

        if attendance.check_out:
            attendance.chkout_location_id = check
        else:
            attendance.chkin_location_id = check
        action_message['action']['attendance'] = attendance.read()[0]
        return action_message

    def _create_hr_geolocation(self, name, latitude, longitude):
        return self.env['hr.geolocation'].create({
            'name': name,
            'latitude': latitude,
            'longitude': longitude
        })

    @api.multi
    def update_attendances(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.attendance.update.wizard',  # this model
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_employee_id':self.id}
        }
