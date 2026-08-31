{
    'name': 'Stock In Report (Excel)',
    'version': '18.0.1.0.0',
    'summary': 'تقرير Excel لمنتجات المخزن الداخلة خلال فترة معينة بالكمية والكوست الاجمالي',
    'category': 'Inventory', 
    'depends': ['stock', 'stock_account'],
    'data': [
        'security/ir.model.access.csv',
        'views/wizard_view.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
