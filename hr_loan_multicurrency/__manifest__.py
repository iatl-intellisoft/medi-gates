# -*- coding: utf-8 -*-
{
    'name': 'Employee Loans - Multi Currency (USD Loans on SDG Payroll)',
    'version': '18.0.1.0.0',
    'category': 'Human Resources/Payroll',
    'summary': 'إدارة قروض الموظفين بعملة مختلفة عن عملة الراتب/الشركة مع دعم العملة الثانوية محاسبيًا',
    'description': """
Employee Loans with Foreign Currency Support
=============================================
- يسمح بتسجيل قرض للموظف بعملة (مثال: USD) مختلفة عن عملة الشركة (مثال: SDG).
- يولّد جدول أقساط تلقائيًا.
- عند احتساب الراتب، يحقن قيمة القسط المستحق (محوّلة لعملة الشركة بسعر الصرف الفعلي في تاريخ
  الراتب) كـ Other Input بكود LOAN، ليستخدمها Salary Rule خاص بالخصم.
- لا يعدّل أي دالة داخلية في hr_payroll / hr_payroll_account. الاعتماد كليًا على آلية
  "Secondary Currency" في account.account لعرض/حفظ amount_currency تلقائيًا على القيود.
- يحتفظ بسجل دقيق لكل قسط: المبلغ بعملة القرض، المبلغ بعملة الشركة، وسعر الصرف المستخدم.
    """,
    'depends': ['hr_payroll', 'hr_payroll_account'],
    'data': [
        'security/ir.model.access.csv',
        'data/hr_loan_data.xml',
        'views/hr_loan_views.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
}
