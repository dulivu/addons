# -*- coding: utf-8 -*-
{
    'name': "Sales [Kanban]",
    'category': 'Tools',
    'summary': """Stages & Sequences in Sale Orders""",
    'description': """Stages & Sequences in Sale Orders""",

    'author': "JLQC",
    'version': '1.0',
    'depends': ['sale'],
    'license': 'OPL-1',
    'currency': 'EUR',
    'price': 9,

    # always loaded
    'images': ['images/main_screenshot.png'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_stage_views.xml',
        'views/sale_order_views.xml',
    ],
}
