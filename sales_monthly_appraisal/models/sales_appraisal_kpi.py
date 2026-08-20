# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, AccessError


class SalesAppraisalKpi(models.Model):
    _name = 'sales.appraisal.kpi'
    _description = 'Sales Appraisal KPI Line'
    _order = 'category_id, sequence, id'

    appraisal_id = fields.Many2one(
        'sales.appraisal', string='Appraisal', required=True,
        ondelete='cascade')
    kpi_definition_id = fields.Many2one(
        'sales.appraisal.kpi.definition', string='KPI', required=True,
        ondelete='restrict')
    category_id = fields.Many2one(
        related='kpi_definition_id.category_id', store=True, string='Category')
    sequence = fields.Integer(related='kpi_definition_id.sequence', store=True)
    weight = fields.Float(
        related='kpi_definition_id.weight', store=True,
        string='Weight within Category (%)')
    evaluator = fields.Selection(
        related='kpi_definition_id.evaluator', store=True, string='Evaluator')
    max_rate = fields.Float(
        related='kpi_definition_id.max_rate', store=True,
        string='Max Rate (%)', digits=(6, 4))

    score = fields.Float(string='Score (%)', digits=(5, 2), default=0.0,
                          help="Score from 0 to 100 given by the evaluator.")
    rate = fields.Float(
        string='Rate (%)', digits=(6, 4), compute='_compute_rate', store=True,
        help="Max Rate x Score / 100")
    comments = fields.Text(string='Comments')

    can_edit = fields.Boolean(string='Can Edit', compute='_compute_can_edit')

    _sql_constraints = [
        ('score_range', 'CHECK(score >= 0 AND score <= 100)',
         'The score must be between 0 and 100.'),
        ('kpi_uniq_per_appraisal', 'unique(appraisal_id, kpi_definition_id)',
         'This KPI is already present on this appraisal.'),
    ]

    @api.depends('max_rate', 'score')
    def _compute_rate(self):
        for line in self:
            line.rate = (line.max_rate or 0.0) * (line.score or 0.0) / 100.0

    def _compute_can_edit(self):
        is_accounting = self.env.user.has_group(
            'sales_monthly_appraisal.group_appraisal_accounting')
        is_sales = self.env.user.has_group(
            'sales_monthly_appraisal.group_appraisal_sales')
        is_manager = self.env.user.has_group(
            'sales_monthly_appraisal.group_appraisal_manager')
        for line in self:
            state = line.appraisal_id.state
            if is_manager:
                line.can_edit = True
            elif line.evaluator == 'accounting':
                line.can_edit = is_accounting and state == 'accounting_review'
            else:
                line.can_edit = is_sales and state in ('draft', 'sales_review')

    @api.constrains('score')
    def _check_score(self):
        for line in self:
            if not (0 <= line.score <= 100):
                raise ValidationError("Score must be between 0 and 100.")

    def write(self, vals):
        """Server-side enforcement (not just UI attrs) that Sales evaluators
        cannot edit the Accounting KPI(s) and vice-versa, mirroring the
        Osman / Yazeed split."""
        if not self.env.user.has_group('sales_monthly_appraisal.group_appraisal_manager') \
                and not self.env.su \
                and {'score', 'comments'} & set(vals.keys()):
            is_accounting = self.env.user.has_group(
                'sales_monthly_appraisal.group_appraisal_accounting')
            is_sales = self.env.user.has_group(
                'sales_monthly_appraisal.group_appraisal_sales')
            for line in self:
                if line.evaluator == 'accounting' and not is_accounting:
                    raise AccessError(_(
                        "Only the Accounting evaluator can update the "
                        "'%s' KPI.") % line.kpi_definition_id.name)
                if line.evaluator == 'sales' and not is_sales:
                    raise AccessError(_(
                        "Only the Sales evaluator can update the "
                        "'%s' KPI.") % line.kpi_definition_id.name)
                if line.evaluator == 'accounting' and line.appraisal_id.state != 'accounting_review':
                    raise AccessError(_(
                        "This KPI can only be edited while the appraisal is "
                        "in the Accounting Review stage."))
                if line.evaluator == 'sales' and line.appraisal_id.state not in ('draft', 'sales_review'):
                    raise AccessError(_(
                        "This KPI can only be edited while the appraisal is "
                        "in Draft or Sales Review stage."))
        return super().write(vals)
