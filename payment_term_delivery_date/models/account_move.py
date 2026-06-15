# -*- coding: utf-8 -*-
import logging

from dateutil.relativedelta import relativedelta

from odoo import models

_logger = logging.getLogger(__name__)

DELIVERY_DATE_OFFSET_DAYS = 15


class AccountMove(models.Model):
    """Override the payment terms recomputation so that any payment term
    line configured with the 'delivery_date_act' option uses
    `delivery_date_act + 15 days` as its due date (date_maturity), instead
    of the standard invoice-date based computation.
    """
    _inherit = 'account.move'

    def _recompute_payment_terms_lines(self):
        # Run the standard Odoo computation first so all payment term
        # lines (date_maturity, amounts, etc.) are generated normally.
        res = super()._recompute_payment_terms_lines()

        for move in self:
            move._apply_delivery_date_act_due_dates()

        return res

    def _apply_delivery_date_act_due_dates(self):
        """Adjust date_maturity on payment-term receivable/payable lines
        whose corresponding payment.term.line is set to
        'delivery_date_act', using delivery_date_act + 15 days.
        """
        self.ensure_one()

        payment_term = self.invoice_payment_term_id
        if not payment_term:
            return

        # Safe check: the delivery_date_act field may not exist if the
        # module that defines it is not installed.
        delivery_date = self._fields.get('delivery_date_act') and self.delivery_date_act
        if not delivery_date:
            return

        pt_lines = payment_term.line_ids.sorted(key=lambda l: l.id)
        delivery_lines = pt_lines.filtered(lambda l: l.value == 'delivery_date_act')
        if not delivery_lines:
            return

        # Receivable/payable installment lines created by the standard
        # computation, ordered the same way the payment term lines are.
        term_aml = self.line_ids.filtered(
            lambda l: l.display_type == 'payment_term'
        ).sorted(key=lambda l: l.date_maturity or l.id)

        if len(term_aml) != len(pt_lines):
            # Mismatch between number of generated lines and configured
            # term lines: skip silently to avoid breaking posting.
            _logger.debug(
                "Payment term lines (%s) and journal items (%s) count "
                "mismatch on move %s; skipping delivery date adjustment.",
                len(pt_lines), len(term_aml), self.display_name,
            )
            return

        new_due_date = delivery_date + relativedelta(days=DELIVERY_DATE_OFFSET_DAYS)

        for pt_line, aml in zip(pt_lines, term_aml):
            if pt_line.value == 'delivery_date_act':
                if aml.date_maturity != new_due_date:
                    aml.date_maturity = new_due_date
