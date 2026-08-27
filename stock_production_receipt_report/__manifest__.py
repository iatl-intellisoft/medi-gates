# -*- coding: utf-8 -*-
{
    'name': 'Production Receipt Cost Report (Excel)',
    'version': '18.0.1.0.0',
    'summary': 'تقرير Excel لكميات وتكلفة المنتجات النازلة للمخزن من الإنتاج',
    'category': 'Manufacturing',
    'author': 'Custom',
    'depends': ['stock', 'mrp', 'stock_account'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/production_receipt_report_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
