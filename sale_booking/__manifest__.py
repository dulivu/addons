# -*- coding: utf-8 -*-
{
    'name': "Sales [Bookings]",
    'category': 'Sales',
    'summary': """Manage bookings from Sale Order""",
    'description': """Manage bookings from Sale Order""",

    'auto_install': True,

    'author': "JLQC",
    'version': '2.0',
    'depends': ['sale'],
    'license': 'OPL-1',
    'currency': 'EUR',
    'price': 49,

    # always loaded
    'images': ['images/main_screenshot.png'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_config_settings.xml',
        'views/sale_views.xml',
        'views/booking_views.xml',
    ],
}
