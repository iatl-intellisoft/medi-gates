# -*- coding: utf-8 -*-
from odoo import api, models, fields, _
from odoo.exceptions import ValidationError


class AccountPaymentTermLine(models.Model):
    """Extend Payment Term Lines with a new due-date computation option
    based on the Actual Delivery Date of the related invoice.
    """
    _inherit = 'account.payment.term.line'

    value = fields.Selection(
        selection_add=[
            ('delivery_date_act', '15 Days After Actual Delivery Date'),
        ],
        ondelete={'delivery_date_act': 'set default'},
    )


class AccountPaymentTerm(models.Model):
    """Override the 100% validation so that lines using the
    'delivery_date_act' option are treated like 'percent' lines when
    checking that the total adds up to 100%.
    """
    _inherit = 'account.payment.term'

    @api.constrains('line_ids')
    def _check_lines(self):
        # Lines whose `value` is one of these are amount-based (contribute
        # to the 100% total). Standard Odoo only recognizes 'percent';
        # we add 'delivery_date_act' to that set.
        percent_like_values = ('percent', 'delivery_date_act')

        for term in self:
            percent_lines = term.line_ids.filtered(
                lambda l: l.value in percent_like_values
            )
            total_percent = sum(percent_lines.mapped('value_amount'))

            if not percent_lines or total_percent != 100:
                raise ValidationError(_(
                    "The Payment Term must have at least one percent line "
                    "and the sum of the percent must be 100%."
                ))

    def _compute_terms(self, *args, **kwargs):
        """Make amount-computation work for 'delivery_date_act' lines.

        Core Odoo's _compute_terms only knows how to compute installment
        amounts for 'percent' and 'fixed' line values. To avoid the issues
        caused by copy_data()/new() on unsaved (NewId) records, we
        temporarily relabel 'delivery_date_act' lines as 'percent'
        in-place (in memory, via a plain Python attribute set - this does
        NOT trigger ORM writes/recomputation), run the core computation,
        then restore the original value.

        The due-date for 'delivery_date_act' lines is corrected afterwards
        in account.move (_apply_delivery_date_act_due_dates), based on
        delivery_date_act + 15 days.
        """
        delivery_lines = self.line_ids.filtered(
            lambda l: l.value == 'delivery_date_act'
        )

        if not delivery_lines:
            return super()._compute_terms(*args, **kwargs)

        # Save originals, temporarily set cache value to 'percent'.
        originals = {line.id: line.value for line in delivery_lines}
        try:
            for line in delivery_lines:
                line.env.cache.set(line, line._fields['value'], 'percent')
            return super()._compute_terms(*args, **kwargs)
        finally:
            for line in delivery_lines:
                line.env.cache.set(
                    line, line._fields['value'], originals[line.id]
                )
