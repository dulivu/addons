# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class FS(models.Model):
    _name = 'covid.fs'

    user_id = fields.Many2one('res.users', 'Usuario')
    date = fields.Date('Fecha')
    q1 = fields.Selection([('si', 'Si'), ('no', 'No')], 'Sensación de alza térmica o fiebre')
    q2 = fields.Selection([('si', 'Si'), ('no', 'No')], 'Tos, estornudos o dificultad para respirar')
    q3 = fields.Selection([('si', 'Si'), ('no', 'No')], 'Expectoración o flema amarilla o verdosa')
    q4 = fields.Selection([('si', 'Si'), ('no', 'No')], 'Contacto con persona(s) con un caso confirmado de COVID-19')
    q6 = fields.Selection([('si', 'Si'), ('no', 'No')], 'Presenta dolor de cabeza (cefalea)')
    q7 = fields.Selection([('si', 'Si'), ('no', 'No')], 'Tiene suelto el estomago (Diarrea)')
    q5 = fields.Selection([('si', 'Si'), ('no', 'No')], 'Estas tomando alguna medicación (debe detallar cuál o cuales)')
    q5a = fields.Char('Detalle')

    employee_id = fields.Many2one('hr.employee', string='Employee', compute='_compute_employee', store=True)
    department_id = fields.Many2one('hr.department', string='Departamento', compute='_compute_employee', store=True)

    @api.depends('user_id')
    @api.multi
    def _compute_employee(self):
        for line in self:
            if line.user_id:
                employee = self.env['hr.employee'].sudo().search([('user_id', '=', line.user_id.id)])
                if employee:
                    line.employee_id = employee.id
                    line.department_id = employee.department_id.id

    @api.multi
    def name_get(self):
        list = []
        for dj in self:
            list.append((dj.id, dj.create_date))
        return list

    @api.model
    def create(self, vals):
        uid = vals.get('user_id', 0)

        question1 = vals.get('question1', False)
        question2 = vals.get('question2', False)
        question3 = vals.get('question3', False)
        question4 = vals.get('question4', False)
        question5 = vals.get('question5', False)
        if question1 or question2 or question3 or question4 or question5:
            employee = self.env['hr.employee'].sudo().search([('user_id', '=', uid)])
            employee.write({'covid_enabled': True})

            template_obj = self.env['mail.mail'].sudo()
            template_data = {
                'subject': 'Notificación de inhabilitación : ' + employee[0].name,
                'body_html': 'Notificación de inhabilitación : ' + employee[0].name,
                'email_from': 'info@ceramicaskantu.com',
                'email_to': ", ".join(['sistemas@ceramicaskantu.com', 'personal@ceramicaskantu.com', 'mccopa@ckantu.com'])
            }
            template_id = template_obj.create(template_data)
            template_id.send(template_id)

        q1 = vals.get('q1', False)
        q2 = vals.get('q2', False)
        q3 = vals.get('q3', False)
        q4 = vals.get('q4', False)
        q5 = vals.get('q5', False)
        date = vals.get('date', False)

        if not date:
            vals.update({'date': fields.Date.today()})

        if q1 is False or q2 is False or q3 is False or q4 is False or q5 is False:
            raise UserError('Debe llenar confirmar todas las preguntas')

        if q1 == 'si' or q2 == 'si' or q3 == 'si' or q4 == 'si' or q5 == 'si':
            employee = self.env['hr.employee'].sudo().search([('user_id', '=', uid)])
            employee.write({'covid_enabled': True})

            template_obj = self.env['mail.mail'].sudo()
            template_data = {
                'subject': 'Notificación de inhabilitación : ' + employee[0].name,
                'body_html': 'Notificación de inhabilitación : ' + employee[0].name,
                'email_from': 'info@ceramicaskantu.com',
                'email_to': ", ".join(
                    ['sistemas@ceramicaskantu.com', 'personal@ceramicaskantu.com', 'mccopa@ckantu.com'])
            }
            template_id = template_obj.create(template_data)
            template_id.send(template_id)

        res = super(FS, self).create(vals)
        return res
