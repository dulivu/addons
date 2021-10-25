# -*- coding: utf-8 -*-
{
    'name': "Attendance Control Time",
    'summary': "Attendance Control Time",

    'description': """
        Control de asistencias:
        - Diferencias de horario en ingreso y salida
        - Calculo del tiempo de refrigerio
        - Actualización de diferencias por empleado según horario
    """,

    'author': "Luis Rodrigo Mejia Mateus",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','hr_attendance'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/web_assets_backend.xml',
        'views/hr_attendance_view.xml',
        'views/resource_view.xml',
        'views/hr_employee_view.xml',
        'wizard/update_attendances.xml',
    ]
}
