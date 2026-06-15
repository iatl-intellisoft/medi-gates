from datetime import timedelta

from odoo import models


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

        sale_order = False

        if move.invoice_origin:
            sale_order = self.env["sale.order"].search(
                [('name', '=', move.invoice_origin)],
                limit=1
            )

        if not sale_order or not sale_order.actual_delivery_date:
            return result

        actual_delivery_date = sale_order.actual_delivery_date

        lines = self.line_ids.sorted(lambda l: l.sequence)

        for index, line in enumerate(lines):

            if (
                line.delay_type == "actual_delivery_date"
                and index < len(result)
            ):
                amount, discount_date = result[index]

                due_date = actual_delivery_date + timedelta(
                    days=line.nb_days
                )

                result[index] = (
                    amount,
                    due_date
                )

        return result