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
        amounts for 'percent' and 'fixed' line values. To avoid touching
        the database, we build an in-memory (non-persisted) copy of `self`
        where 'delivery_date_act' lines are relabelled as 'percent' (same
        value_amount), run the core computation on that copy, and return
        its result. The due-date for 'delivery_date_act' lines is corrected
        afterwards in account.move (_apply_delivery_date_act_due_dates),
        based on delivery_date_act + 15 days.
        """
        delivery_lines = self.line_ids.filtered(
            lambda l: l.value == 'delivery_date_act'
        )

        if not delivery_lines:
            return super()._compute_terms(*args, **kwargs)

        # Build in-memory copies of the payment term lines, relabelling
        # 'delivery_date_act' as 'percent' so the core logic treats them
        # as ordinary percentage-based installments.
        new_line_vals = []
        for line in self.line_ids:
            vals = line.copy_data()[0]
            vals['payment_id'] = self.id
            if line.value == 'delivery_date_act':
                vals['value'] = 'percent'
            new_line_vals.append(vals)

        temp_term = self.new({
            **self.copy_data()[0],
            'line_ids': [(0, 0, vals) for vals in new_line_vals],
        })

        return super(AccountPaymentTerm, temp_term)._compute_terms(*args, **kwargs)
