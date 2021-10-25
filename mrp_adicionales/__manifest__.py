# -*- coding: utf-8 -*-
{
    'name': "mrp_adicionales",

    'summary': """
        Modulo para el pago de servicios adicioanles, descuentos,
        bonos y sueldos fijos""",

    'description': """
        Pago de adicionales
    """,

    'author': "Barce",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Pagos',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mrp_kantu'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/mrp_adicionales.xml',
        'views/mrp_descuentos.xml',
        'views/mrp_bonus.xml',
    ],
    # only loaded in demonstration mode
}