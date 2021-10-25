# -*- coding: utf-8 -*-
{
    'name': "Mrp Serigrafia",
    'summary': """
        Modulo de serigrafia para Ceramicas kantu""",
    'author': "Luis Rodrigo Mejia Mateus",
    'category': 'Manufacturing',
    'depends': ['base', 'mrp', 'mrp_kantu'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'report/mesh_production.xml',
        'views/product_template.xml',
        'views/mrp_production.xml',
        'views/serigraphy_pay_menu.xml',
        'views/mrp_group_pay.xml',
        'views/mrp_periodo.xml',
    ]
}
