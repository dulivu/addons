# -*- coding: utf-8 -*-

from odoo import models, fields, api


class DJ(models.Model):
    _name = 'covid.dj'

    employee_id = fields.Many2one('hr.employees', 'Colaborador')
    user_id = fields.Many2one('res.users', 'Usuario')
    date = fields.Date('Fecha', required=True, default=fields.Date.today())
    # ¿Sufre de alguna de estas condiciones?
    question1a = fields.Boolean('Hipertensión arterial (HTA)')
    question1b = fields.Boolean('Diabetes')
    question1c = fields.Boolean('Cáncer (cualquier grado u organo)')
    question1d = fields.Boolean('Inmunodeficiencia (incluye VIH-SIDA)')
    question1e = fields.Boolean('Gestante (indicar semana de gestación)')
    question1f = fields.Boolean('Asma')
    question1g = fields.Boolean('Enfermedades Cardiacas')
    question1h = fields.Boolean('Enfermedades Pulmonares')
    question1i = fields.Boolean('Enfermedades renales (riñones)')
    question1j = fields.Boolean('Enfermedades neurologicas')
    question1k = fields.Boolean('Obesidad IMC>30')
    question1l = fields.Boolean('Otros (especificar)')
    question1m = fields.Boolean('Ninguna')
    question1_obs = fields.Char('Especificar')

    q1a = fields.Selection([('si', 'Si'), ('no', 'No')], 'Obesidad')
    q1b = fields.Selection([('si', 'Si'), ('no', 'No')], 'Enfermedad pulmonar crónica')
    q1c = fields.Selection([('si', 'Si'), ('no', 'No')], 'Diabetes')
    q1d = fields.Selection([('si', 'Si'), ('no', 'No')], 'Hipertensión arterial')
    q1e = fields.Selection([('si', 'Si'), ('no', 'No')], 'Embarazo/puerperino')
    q1f = fields.Selection([('si', 'Si'), ('no', 'No')], 'Mayor de 60 años')
    q1g = fields.Selection([('si', 'Si'), ('no', 'No')], 'Insuficiencia renal crónica')
    q1h = fields.Selection([('si', 'Si'), ('no', 'No')], 'Enfermedades cardiovasculares')
    q1i = fields.Selection([('si', 'Si'), ('no', 'No')], 'Asma')
    q1j = fields.Selection([('si', 'Si'), ('no', 'No')], 'Enfermedad o tratamiento inmunosupresor')
    q1k = fields.Selection([('si', 'Si'), ('no', 'No')], 'Cancer')
    q1l = fields.Selection([('si', 'Si'), ('no', 'No')], 'Personal de salud')
    q1m = fields.Selection([('si', 'Si'), ('no', 'No')], 'Otros (especificar)')
    q1ma = fields.Char('Especificar')

    question2 = fields.Boolean('¿Tuvo contacto con una persona enferma o sospechosa de coronavirus (COVID-19)?')
    question2_rel = fields.Char('Parentesco')
    question2_name = fields.Char('Nombre')
    question3 = fields.Boolean(
        '¿Ha estado en algún lugar con alta concurrencia de personas (hospitales, clínicas, mercados, otros) SIN USAR MASCARILLA Y REALIZAR LAS MEDIDAS DE HIGIENE NECESARIAS PARA EVITAR EL CONTAGIO?')

    q2 = fields.Selection([('si', 'Si'), ('no', 'No')], '¿En los últimos 14 días ha tenido contacto con personas con diagnóstico confirmado de Coronavirus?')
    q2a = fields.Boolean('Entorno familiar')
    q2b = fields.Boolean('Entorno laboral')
    q2c = fields.Boolean('Entorno de salud')

    q3 = fields.Selection([('si', 'Si'), ('no', 'No')], '¿Ha viajado fuera del país o zonas de Perú con casos confirmados de COVID-19. En los últimos 14 días?')
    q3a = fields.Char('País que ha visitado')
    q3b = fields.Date('Fecha de retorno al país')

    q5 = fields.Selection([('si', 'Si'), ('no', 'No')], '¿En los últimos 14 días se desplazó a diferentes distritos, distintos a su lugar de residencia?')
    q5a = fields.Char('¿Qué distritos visitó?')

    # En la casa donde habita tiene los siguientes grupos de riesgo
    q6a = fields.Boolean('Adulto mayor')
    q6b = fields.Boolean('Niño')
    q6c = fields.Boolean('Gestante')
    q6d = fields.Boolean('Familiar con enfermedad crónica')

    # ¿Presenta algunos de estos síntomas actualmente o durante el periodo de cuarentena?
    question4k = fields.Boolean('Ninguno')
    question4a = fields.Boolean('Tos')
    question4b = fields.Boolean('Malestar general')
    question4c = fields.Boolean('Dolor de garganta')
    question4d = fields.Boolean('Fiebre (T° > 38°C)')
    question4e = fields.Boolean('Secreción o Congestión Nasal')
    question4f = fields.Boolean('Dolor de cabeza (cefalea)')
    question4g = fields.Boolean('Dolor muscular y/o en articulaciones')
    question4h = fields.Boolean('Dificultad respiratoria')
    question4i = fields.Boolean('Estornudos')
    question4j = fields.Boolean('Diarrea')
    question4_obs = fields.Date('Fecha de inicio (desde el primer síntoma)')

    q4a = fields.Boolean('Fiebre')
    q4b = fields.Boolean('Dificultad para respirar (Disnea)')
    q4c = fields.Boolean('Tos seca o productiva')
    q4d = fields.Boolean('Dolor de garganta')
    q4e = fields.Boolean('Congestión nasal')
    q4f = fields.Boolean('Fatiga')
    q4g = fields.Boolean('Dolor de músculos y/o articulaciones')
    q4h = fields.Boolean('Dolor de cabeza')
    q4i = fields.Boolean('Escalofríos')
    q4j = fields.Boolean('Nauseas o vómitos')
    q4k = fields.Boolean('Diarrea')
    q4l = fields.Boolean('Ninguno')
    q4_date = fields.Date('Fecha de inicio de los síntomas')

    question5 = fields.Char('Si está tomando alguna medicina actualmente, indique cual (Si no, dejar en blanco)')
    question6 = fields.Boolean('Durante la cuarentena ¿fuiste considerado como caso sospechoso, probable o confirmado para COVID19?')

    question7 = fields.Boolean('He recibido explicación del objetivo de esta evaluación y me comprometo a responder con la verdad')

    doc_type = fields.Selection([('dni', 'DNI'), ('card', 'Carnet de extranjería'), ('other', 'Otro')], 'Tipo de documento')
    doc_num = fields.Char('Número de documento')
    age = fields.Integer('Edad')
    gender = fields.Selection([('male', 'Masculino'), ('female', 'Femenino')], 'Sexo')
    work = fields.Char('Puesto de trabajo')
    employeer = fields.Many2one('res.company', string="Empleador")
    country = fields.Char('Nacionalidad')
    departamento = fields.Char('Departamento de residencia')
    provincia = fields.Char('Provincia de residencia')
    distrito = fields.Char('Distrito de residencia')
    direc = fields.Char('Dirección actual de residencia')
    email = fields.Char('Correo electrónico')
    cel = fields.Char('Celular')
    phone = fields.Char('Teléfono fijo')
    familiar = fields.Char('Datos de algún familiar de contacto')
    familiar_cel = fields.Char('Celular')
    familiar_work = fields.Selection([('visit', 'Visita'), ('temp', 'Temporal'), ('perm', 'Permanente')], 'Tipo de trabajo')


    @api.multi
    def name_get(self):
        list = []
        for dj in self:
            list.append((dj.id, dj.create_date))
        return list

    @api.model
    def create(self, vals):
        uid = vals.get('user_id', 0)

        question1a = vals.get('question1a', False)
        question1b = vals.get('question1b', False)
        question1c = vals.get('question1c', False)
        question1d = vals.get('question1d', False)
        question1e = vals.get('question1e', False)
        question1f = vals.get('question1f', False)
        question1g = vals.get('question1g', False)
        question1h = vals.get('question1h', False)
        question1i = vals.get('question1i', False)
        question1j = vals.get('question1j', False)
        question1k = vals.get('question1k', False)
        question1l = vals.get('question1l', False)
        question1 = question1a or question1b or question1c or question1d \
                    or question1e or question1f or question1g or question1h \
                    or question1i or question1j or question1k or question1l

        question2 = vals.get('question2', False)
        question3 = vals.get('question3', False)

        question4a = vals.get('question4a', False)
        question4b = vals.get('question4a', False)
        question4c = vals.get('question4a', False)
        question4d = vals.get('question4a', False)
        question4e = vals.get('question4a', False)
        question4f = vals.get('question4a', False)
        question4g = vals.get('question4a', False)
        question4h = vals.get('question4a', False)
        question4i = vals.get('question4a', False)
        question4j = vals.get('question4a', False)
        question4 = question4a or question4b or question4c or question4d \
                    or question4e or question4f or question4g or question4h \
                    or question4i or question4j

        question5 = vals.get('question5', False)
        question6 = vals.get('question6', False)

        if question1 or question2 or question3 or question4 or question5 or question6:
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

        # NEW
        q4a = vals.get('q4a', False)
        q4b = vals.get('q4b', False)
        q4c = vals.get('q4c', False)
        q4d = vals.get('q4d', False)
        q4e = vals.get('q4e', False)
        q4f = vals.get('q4f', False)
        q4g = vals.get('q4g', False)
        q4h = vals.get('q4h', False)
        q4i = vals.get('q4i', False)
        q4j = vals.get('q4j', False)
        q4k = vals.get('q4k', False)
        q4 = q4a or q4b or q4c or q4d or q4e or q4f or q4g or q4h or q4i or q4j or q4k

        q1a = vals.get('q1a', False)
        q1b = vals.get('q1b', False)
        q1c = vals.get('q1c', False)
        q1d = vals.get('q1d', False)
        q1e = vals.get('q1e', False)
        q1f = vals.get('q1f', False)
        q1g = vals.get('q1g', False)
        q1h = vals.get('q1h', False)
        q1i = vals.get('q1i', False)
        q1j = vals.get('q1j', False)
        q1k = vals.get('q1k', False)
        q1l = vals.get('q1l', False)
        q1 = q1a == 'si' or q1b == 'si' or q1c == 'si' or q1d == 'si' or q1e == 'si' or q1f == 'si' or q1g == 'si' or q1h == 'si' or q1i == 'si' or q1j == 'si' or q1k == 'si' or q1l == 'si'

        if not vals.get('date', False):
            vals.update({'date': fields.Date.today()})

        if vals.get('q2', False) == 'si' or q1 or q4 or vals.get('q3', False) == 'si':
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

        res = super(DJ, self).create(vals)
        return res
