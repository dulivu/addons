# -*- coding: utf-8 -*-
{
    'name': "ZkTeco, Actualizar base de datos",

    'summary': """
        Recuperar marcaciones de la base de datos de reloj ZK""",
    'description': """
        Recupera marcaciones de una base de datos MSSQL que siga la estructura que tienen los relojes ZK""",

    'author': "Jorge Luis Quico C.",
    'website': '',

    'category': 'Tools',
    'version': '0.1',
    'depends': ['hr_attendance'],
    'application': False,

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views.xml',
        'report.xml',
        #'report/holiday_report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
