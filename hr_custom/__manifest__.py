# -*- coding: utf-8 -*-
###############################################################################
#
#    IATL-Intellisoft International Pvt. Ltd.
#    Copyright (C) 2021 Tech-Receptives(<http://www.iatl-intellisoft.com>).
#
###############################################################################

{
    'name': "HR Custom",

    'summary': """
        """,

    'description': """
        
    """,
    'author': "IATL Intellisoft International",
    'website': "http://www.iatl-intellisoft.com",
    'category': 'Human Resource',
    'version': '18.0.1.0.0',
    'depends': ['hr', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/hr_views.xml',
        'views/res_config_settings.xml',
        'views/account_move_views.xml',
    ],
}
