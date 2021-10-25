# -*- coding: utf-8 -*-
{
    'name': "Covid (Kantu)",
    'summary': """Módulo de registro y control covid""",
    'description': """Módulo de registro y control covid""",
    'author': "Ceramicas Kantu S.A.C. (Jorge Quico)",
    'website': "http://www.ceramicaskantu.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'hr', 'mail', 'hr_holidays'],
    'qweb': ['views/buttons.xml'],
    'data': [
        'security/ir.model.access.csv',
        'security/covid_security.xml',
        'views/reports.xml',
        'views/menus.xml',
        'views/forms.xml',
        'views/searchs.xml',
        'views/trees.xml',
    ]
}
