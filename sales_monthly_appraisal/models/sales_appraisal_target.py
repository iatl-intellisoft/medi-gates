# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError

MONTH_SELECTION = [
    ('01', 'January'), ('02', 'February'), ('03', 'March'),
    ('04', 'April'), ('05', 'May'), ('06', 'June'),
    ('07', 'July'), ('08', 'August'), ('09', 'September'),
    ('10', 'October'), ('11', 'November'), ('12', 'December'),
]


class SalesAppraisalTarget(models.Model):
    _name = 'sales.appraisal.target'
    _description = 'Sales Monthly Collection Target'
    _order = 'year desc, month desc, salesperson_id'
    _rec_name = 'display_name'

    salesperson_id = fields.Many2one(
        'res.users', string='Salesperson', required=True,
        domain=[('share', '=', False)])
    month = fields.Selection(MONTH_SELECTION, string='Month', required=True)
    year = fields.Integer(string='Year', required=True,
                           default=lambda self: fields.Date.today().year)
    collection_target = fields.Monetary(string='Collection Target', required=True)
    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.company.currency_id.id)
    company_id = fields.Many2one(
        'res.company', default=lambda self: self.env.company, required=True)
    display_name = fields.Char(compute='_compute_display_name', store=True)

    _sql_constraints = [
        ('target_uniq', 'unique(salesperson_id, month, year, company_id)',
         'Only one collection target is allowed per salesperson per month.'),
    ]

    @api.depends('salesperson_id', 'month', 'year')
    def _compute_display_name(self):
        month_labels = dict(MONTH_SELECTION)
        for rec in self:
            rec.display_name = "%s - %s/%s" % (
                rec.salesperson_id.name or '',
                month_labels.get(rec.month, rec.month or ''),
                rec.year or '')

    @api.constrains('collection_target')
    def _check_target_positive(self):
        for rec in self:
            if rec.collection_target < 0:
                raise ValidationError("Collection Target cannot be negative.")
