# -*- coding: utf-8 -*-
{
    'name': "Mi Reporte de Asistencia",

    'summary': """
        Registro de asistencias del personal """,

    'author': "Luis Rodrigo Mejia Mateus",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Huaman Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr_attendance','hr_att_control_time'],

    # always loaded
    'data': [
        'views/my_report.xml',
        'views/assets_backend.xml',
    ],
    'qweb': [
        'static/src/xml/my_attendance_report.xml'
    ]
}