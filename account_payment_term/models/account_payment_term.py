from odoo import fields, models
from datetime import timedelta

class AccountPaymentTerm(models.Model):
    _inherit = "account.payment.term"

    def _compute_terms(
        self,
        date_ref,
        currency,
        company,
        tax_amount,
        tax_amount_currency,
        sign,
        untaxed_amount,
        untaxed_amount_currency,
        cash_rounding=None,
    ):
        result = super()._compute_terms(
            date_ref,
            currency,
            company,
            tax_amount,
            tax_amount_currency,
            sign,
            untaxed_amount,
            untaxed_amount_currency,
            cash_rounding,
        )

        move = self.env.context.get("move")

        if not move:
            return result

        if not move.delivery_date_act:
            return result

        lines = self.line_ids.sorted("sequence")

        for index, line in enumerate(lines):

            if (
                line.delay_type == "actual_delivery"
                and index < len(result)
            ):

                amount, due_date = result[index]

                result[index] = (
                    amount,
                    move.delivery_date_act + timedelta(days=line.nb_days)
                )

        return result
