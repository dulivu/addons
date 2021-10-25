# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Tipo de Cambio Dolar Peru',
    'version': '1.0',
    'category': 'Accounting',
    'description': """Importa el tipo de cambio del dolar para Peru.
""",
    'depends': [
        'account',
    ],
    'data': [
        'views/account_config_setting_view.xml',
        'views/service_cron_data.xml',
    ],
    'installable': True,
}
