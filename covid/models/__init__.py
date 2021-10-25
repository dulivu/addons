# -*- coding: utf-8 -*-

from . import dj
from . import fs
from . import hr_employee
from . import imc
from . import temp
from odoo import models, fields, api
from odoo.exceptions import UserError
import time


class CovidTempSummary(models.TransientModel):
    _name = 'covid.temp.summary.employee'
    _description = ''

    date_from = fields.Date(string='Desde', required=True, default=lambda *a: time.strftime('%Y-%m-01'))
    date_to = fields.Date(string='Hasta', required=True, default=lambda *a: time.strftime('%Y-%m-01'))
    emp = fields.Many2many('hr.employee', 'summary_covid_temp_rel', 'sum_id', 'emp_id', string='Employee(s)')

    @api.multi
    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        data['emp'] = self.env.context.get('active_ids', [])
        employees = self.env['hr.employee'].browse(data['emp'])
        datas = {
            'ids': [],
            'model': 'hr.employee',
            'form': data
        }
        return self.env['report'].get_action(employees, 'covid.template_report_temp_summary', data=datas)


class CovidTempSummaryDept(models.TransientModel):

    _name = 'covid.temp.summary.dept'

    date_from = fields.Date(string='From', required=True, default=lambda *a: time.strftime('%Y-%m-01'))
    date_to = fields.Date(string='Hasta', required=True, default=lambda *a: time.strftime('%Y-%m-01'))
    depts = fields.Many2many('hr.department', 'summary_covid_temp_dept_rel', 'sum_id', 'dept_id', string='Department(s)')

    @api.multi
    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        if not data.get('depts'):
            raise UserError(_('Tiene que seleccionar por lo menos un departamento. Vuelva a intentarlo.'))
        departments = self.env['hr.department'].browse(data['depts'])
        datas = {
            'ids': [],
            'model': 'hr.department',
            'form': data
        }
        return self.env['report'].get_action(departments, 'covid.template_report_temp_summary', data=datas)
