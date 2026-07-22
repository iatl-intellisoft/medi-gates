# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, AccessError, RedirectWarning



class OrderReturn(models.Model):
    _inherit = 'order.return'

    purchase_id = fields.Many2one("purchase.order", string="Purchase", required=False, store=True)
    purchase_picking_id = fields.Many2one("stock.picking", string="Return Picking", required=False, )
    purchase_tax_ids = fields.Many2many('account.tax', string='Taxes',
                                        domain=['|', ('active', '=', False), ('active', '=', True)])

    inv_created = fields.Boolean('Bill Created')

    @api.onchange('purchase_picking_id')
    def _onchange_purchase_picking_id(self):
        self.picking_id = self.purchase_picking_id.id

    @api.onchange('purchase_id')
    def _onchange_purchase_id(self):
        for rec in self:
            rec.origin = rec.purchase_id.name
            rec.partner_id = rec.purchase_id.partner_id.id

    

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals['name'] == _('New'):
                if vals['return_type'] == 'sale':
                    vals['name'] = self.env['ir.sequence'].next_by_code('sale.return') or _('New')
        return super(OrderReturn, self).create(vals_list)

    # @api.model_create_multi
    # def create(self, vals):
    #     if not vals.get('name') or vals['name'] == _('New'):
    #         if vals['return_type'] == 'purchase':
    #             vals['name'] = self.env['ir.sequence'].next_by_code('purchase.return') or _('New')
    #     return super(OrderReturn, self).create(vals)

    def _prepare_invoice_po(self):
        """
        Prepare the dict of values to create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        if self.return_type == 'purchase':

            self.ensure_one()
            # journal = self.env['account.move'].with_context(default_move_type='in_invoice')._search_default_journal()
            journal = self.env['account.journal'].search([
                ('type', '=', 'purchase'),
                ('company_id', '=', self.company_id.id)
                ], limit=1)
            if not journal:
                raise UserError(_('Please define an accounting Purchase journal for the company %s (%s).') % (
                    self.company_id.name, self.company_id.id))

            invoice_vals = {
                'ref': self.purchase_id.partner_ref or '',
                'move_type': 'in_refund',
                'narration': self.purchase_id.notes,
                'currency_id': self.currency_id.id,
                # 'invoice_user_id': self.purchase_id.user_id and self.purchase_id.user_id.id,
                'partner_id': self.partner_id.id,
                'fiscal_position_id': self.purchase_id.fiscal_position_id,
                'partner_bank_id': self.company_id.partner_id.bank_ids[:1].id,
                'journal_id': journal.id,  # company comes from the journal
                'invoice_origin': self.name,
                'invoice_payment_term_id': self.purchase_id.payment_term_id.id,
                'payment_reference': _('Reversal of: %(name)s, %(reason)s', name=self.name, reason=self.reason_id),
                'invoice_line_ids': [],
                'company_id': self.company_id.id,
                'return_order_id': self.id,
                'purchase_id': self.purchase_id.id,
            }
            return invoice_vals

    def action_reverse_po(self):
        if self.return_type == 'purchase':
            invoice_line_vals = []
            invoice_vals_list = []
            invoice_vals = self._prepare_invoice_po()
            for line in self.return_line:
                if line.purchase_order_id:
                    invoice_line_vals.append(
                        (0, 0, line._prepare_invoice_line_po()), )

            invoice_vals['invoice_line_ids'] = invoice_line_vals
            invoice_vals_list.append(invoice_vals)

            invoice_reverse = self.env['account.move'].create(invoice_vals_list)
            for move in invoice_reverse:
                move.message_post_with_source('mail.message_origin_link',
                    render_values={'self': move, 'origin': self},
                    subtype_xmlid='mail.mt_note',
                )

                # move.message_post_with_view('mail.message_origin_link',
                #                             values={'self': move,
                #                                     'origin': self},
                #                             subtype_id=self.env.ref('mail.mt_note').id
                #                             )

            new_moves = []
            new_invoice_line_ids = []
            self.inv_created = True


class OrderReturnLine(models.Model):
    _inherit = 'order.return.line'

    purchase_order_id = fields.Many2one('purchase.order.line', string='Purchase Order', )

    def _prepare_invoice_line_po(self, move=False):
        self.ensure_one()
        journal = self.env['account.move'].with_context(default_move_type='in_invoice')._search_default_journal()
        if not journal:
            raise UserError(_('Please define an accounting sales journal for the company %s (%s).') % (
                self.company_id.name, self.company_id.id))
        move_line_vals = {
            'display_type': self.purchase_order_id.display_type or 'product',
            'sequence': self.purchase_order_id.sequence,
            'product_id': self.product_id.id,
            'name': self.name,
            'quantity': self.qty_return,
            'price_unit': self.price_unit,
            # 'analytic_account_id': self.purchase_order_id.account_analytic_id.id,
            # 'analytic_tag_ids': [(6, 0, self.purchase_order_id.analytic_tag_ids.ids)],
            'purchase_line_id': self.purchase_order_id.id,
            'purchase_order_id': self.purchase_order_id.order_id.id,
            'account_id': self.product_id.categ_id.return_purchase_account.id,
            'discount': self.discount,
            'analytic_distribution': self.analytic_distribution,
            'tax_ids': [(6, 0, self.tax_ids.ids)],

        }
        if not move:
            return move_line_vals
        move_line_vals.update({
            'move_id': move.id,
        })
        return move_line_vals
