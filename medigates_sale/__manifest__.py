# -*- coding: utf-8 -*-
{
    'name': "Medigates Sale Custom",

    'summary': """
        """,

    'description': """
    """,

    'author': "IATL International",
    'website': "http://www.iatl-sd.com",
    'category': 'Sales',
    'depends': ['base', 'sale', 'account'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/sale_order.xml',
    ],

    'installable': True,
    'application': False,
    'auto_install': False,
}
