# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SalesAppraisalKpiDefinition(models.Model):
    _name = 'sales.appraisal.kpi.definition'
    _description = 'Sales Appraisal KPI Definition'
    _order = 'category_id, sequence, id'

    name = fields.Char(string='KPI', required=True, translate=True)
    category_id = fields.Many2one(
        'sales.appraisal.kpi.category', string='Category', required=True,
        ondelete='restrict')
    sequence = fields.Integer(default=10)
    weight = fields.Float(
        string='Weight within Category (%)', digits=(5, 2), required=True,
        default=100.0,
        help="Weight of this KPI relative to the other KPIs of the same "
             "category. The weights of all active KPIs in one category "
             "should add up to 100%.")
    evaluator = fields.Selection(
        [('sales', 'Sales'), ('accounting', 'Accounting')],
        string='Evaluator', required=True,
        help="Who is allowed to score this specific KPI. Defaults to the "
             "category's evaluator but can be overridden per KPI.")
    max_rate = fields.Float(
        string='Max Rate (%)', digits=(6, 4), compute='_compute_max_rate',
        store=True,
        help="Maximum percentage points this KPI can contribute when scored "
             "100%. Computed as Category Max Rate x Weight / 100.")
    active = fields.Boolean(default=True)
    description = fields.Text(string='Description / Scoring Guidance')

    _sql_constraints = [
        ('weight_positive', 'CHECK(weight >= 0)',
         'The weight must be zero or positive.'),
    ]

    @api.depends('category_id.max_rate', 'weight')
    def _compute_max_rate(self):
        for kpi in self:
            kpi.max_rate = (kpi.category_id.max_rate or 0.0) * (kpi.weight or 0.0) / 100.0

    @api.onchange('category_id')
    def _onchange_category_id(self):
        if self.category_id and not self.evaluator:
            self.evaluator = self.category_id.evaluator

    @api.constrains('category_id', 'weight', 'active')
    def _check_category_weight_total(self):
        """Soft-guard: warn (raise) only when weights clearly exceed 100%,
        to avoid blocking legitimate partial/staged configuration."""
        categories = self.mapped('category_id')
        for category in categories:
            kpis = self.env['sales.appraisal.kpi.definition'].search([
                ('category_id', '=', category.id),
                ('active', '=', True),
            ])
            total_weight = sum(kpis.mapped('weight'))
            if total_weight > 100.01:
                raise ValidationError(
                    "The total weight of active KPIs in category '%s' is "
                    "%.2f%%, which exceeds 100%%. Please adjust the weights."
                    % (category.name, total_weight)
                )
