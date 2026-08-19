# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SalesAppraisalKpiCategory(models.Model):
    _name = 'sales.appraisal.kpi.category'
    _description = 'Sales Appraisal KPI Category'
    _order = 'sequence, id'

    name = fields.Char(string='Category', required=True, translate=True)
    code = fields.Char(string='Code', required=True,
                        help="Technical code, e.g. quantitative, administrative, "
                             "guarantee_collection, deduction")
    sequence = fields.Integer(default=10)
    max_rate = fields.Float(
        string='Max Rate (%)', digits=(6, 4), required=True,
        help="Maximum percentage points this category can contribute to the "
             "Final Rate when all its KPIs score 100%.")
    evaluator = fields.Selection(
        [('sales', 'Sales'), ('accounting', 'Accounting')],
        string='Default Evaluator', required=True, default='sales',
        help="Who is normally responsible for scoring KPIs in this category. "
             "Individual KPI definitions can override this.")
    kpi_definition_ids = fields.One2many(
        'sales.appraisal.kpi.definition', 'category_id', string='KPIs')
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'The category code must be unique.'),
    ]

    @api.constrains('max_rate')
    def _check_max_rate(self):
        for cat in self:
            if cat.max_rate < 0:
                raise ValidationError(
                    "Max Rate cannot be negative for category %s." % cat.name)
