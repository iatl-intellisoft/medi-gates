# -*- coding: utf-8 -*-
{
    'name': "Purchase Order Return",

    'summary': """
        """,

    'description': """
        
    """,

    'author': "IATL International",
    'website': "http://www.iatl-sd.com",
    'license': "AGPL-3",
    'category': "Purchase",
    'version': '0.1',

    'depends': ['purchase_stock', 'order_return'],
    'data': [
        # 'security/ir.model.access.csv',
        'data/return_sequense.xml',
        'wizard/order_return_picking_views.xml',
        'views/order_return_views.xml',
        'views/purchase_views.xml',
        'views/product_category_view.xml',

    ],
}
