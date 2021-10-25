# -*- coding: utf-8 -*-
{
    'name': "HR Attendance Geolocation",

    'summary': """
        Geolocalizacion en el registro de asistencia""",

    'description': """
        Modulo que guarda el registro y visualiza mediante un mapa la localizacion del registro
        de asistencia de los empleados.
        - Requiere de la libreria googlemaps
            instalacion
            $ pip install -U googlemaps
    """,

    'author': "Luis Rodrigo Mejia Mateus",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','resource','hr_attendance'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/web_assets_backend.xml',
        #'views/hr_attendance_view.xml',
        'views/hr_geolocation_view.xml',
    ],
    'qweb': [
        'static/src/xml/coordinates_widget.xml',
        'static/src/xml/my_attendance.xml'
    ],
    'images': [
        # 'static/logo.png',
    ],
}
