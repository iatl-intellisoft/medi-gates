# -*- coding: utf-8 -*-
{
    'name': "Medigates account Custom",

    'summary': """
        """,

    'description': """
    """,

    'author': "IATL International",
    'website': "http://www.iatl-sd.com",
    'category': 'Sales',
    'depends': ['base', 'account','stock', 'sale_stock'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/account.xml',
    ],

    'installable': True,
    'application': False,
    'auto_install': False,
}
