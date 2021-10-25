# -*- coding: utf-8 -*-
{
    'name': "Decor San Blas",

    'summary': """
        Modulo de personalizacion Decor San Blas""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Ceramicas Kantu S.A.C.",
    'website': "http://www.ceramicaskantu.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock'],

    # always loaded
    'data': [
        # 'views/stock_picking_type.xml',
        'views/account_report.xml',
        'views/stock_picking_report.xml',
        'views/stock_picking.xml',
        'views/product_template.xml',
        'views/account_invoice.xml',
        # 'views/template.xml'
    ]
}
