# -*- coding: utf-8 -*-
import googlemaps
from odoo import models, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def _state_is_check_out(self):
        try:
            hr_attendance = self.env['hr.attendance'].search([('employee_id', '=', self.id)], limit=1)
            if hr_attendance.check_out:
                is_check_out = (True, hr_attendance)
            else:
                is_check_out = (False, hr_attendance)
        except:
            is_check_out = False
        return is_check_out

    def _get_name_of_location(self, latitude, longitude):
        if (latitude is not None) and (longitude is not None):
            api_key = self.env['ir.config_parameter'].get_param('google_maps_api_key.att', default='')
            gmaps = googlemaps.Client(key=api_key)
            return gmaps.reverse_geocode((float(latitude), float(longitude)))[0]['formatted_address']
        else:
            return 'Desconocido'

    @api.multi
    def attendance_geolocation(self, dt, type="I", latitude=None, longitude=None, photo=None):
        self.ensure_one()
        location = {
            'name': self._get_name_of_location(latitude, longitude),
            'latitude': latitude,
            'longitude': longitude,
            'photo': photo
        }
        is_checkout, hr_attendance = self._state_is_check_out()

        if type == "I" and is_checkout:
            check_duplicate = self.env['hr.attendance'].search([('employee_id', '=', self.id), ('check_in', '=', dt)])
            if len(check_duplicate) == 1:
                return True
            else:
                hr_location = self.env['hr.geolocation'].create(location)
                hr_attendance = self.env['hr.attendance'].create({
                    'employee_id': self.id,
                    'check_in': dt,
                    'chkin_location_id': hr_location.id
                })
        elif type == 'I' and not is_checkout:
            check_duplicate = self.env['hr.attendance'].search([('employee_id', '=', self.id), ('check_in', '=', dt)])
            if len(check_duplicate) == 1:
                return True
            else:
                hr_attendance.auto_checkout()
                hr_location = self.env['hr.geolocation'].create(location)
                hr_attendance = self.env['hr.attendance'].create({
                    'employee_id': self.id,
                    'check_in': dt,
                    'chkin_location_id': hr_location.id
                })
        elif type == 'O' and not is_checkout:
            hr_location = self.env['hr.geolocation'].create(location)
            hr_attendance.write({
                'check_out': dt,
                'chkout_location_id': hr_location.id
            })
        elif type == 'O' and is_checkout:
            return True
        return hr_attendance.read()[0]
