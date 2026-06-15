# -*- coding: utf-8 -*-
{
    'name': 'Payment Term: Actual Delivery Date',
    'version': '18.0.1.0.0',
    'category': 'Accounting/Accounting',
    'summary': 'Add a payment term option based on the Actual Delivery Date (delivery_date_act)',
    'description': """
Payment Term Based on Actual Delivery Date
===========================================

This module adds a new "Due Date" computation option to Payment Terms:

    - 15 Days After Actual Delivery Date

When a Customer Invoice (account.move) is generated with a Payment Term that
uses this option, the system reads the value of the `delivery_date_act` field
on the invoice and computes the installment's due date as:

    due_date = delivery_date_act + 15 days

This is useful for businesses whose payment terms are contractually tied to
the actual delivery of goods/services rather than the invoice date.

Features
--------
* New selectable option in Payment Term Lines: "15 Days After Actual Delivery Date"
* Automatic recomputation of the due date (date_maturity) on the invoice's
  payment term lines based on `delivery_date_act`
* Works with the standard Odoo 18 payment terms engine (account.move /
  account.payment.term)
* Safe fallback: if `delivery_date_act` is not set, standard Odoo logic applies

Requirements
------------
This module expects a `delivery_date_act` Date field to already exist on
`account.move` (provided by another installed module). If the field does not
exist, this module will not affect anything.
    """,
    'license': 'LGPL-3',
    'depends': ['account', 'sale'],
    'data': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
