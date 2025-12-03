from odoo import models, api, fields
from odoo.exceptions import UserError

class AccountMoveReversal(models.TransientModel):
    _inherit = 'account.move.reversal'

    # def reverse_moves(self, is_modify=False, **kwargs):
    #     '''Extend refund behavior to adjust commissions (supports partial refunds).'''
    #     res = super().reverse_moves()
    #
    #     refund_ids = res.get('res_id')
    #     if not refund_ids:
    #         return res
    #
    #     refunds = self.env['account.move'].browse(refund_ids)
    #
    #     for refund in refunds:
    #         # Only handle customer credit notes (out_refund)
    #         if refund.move_type != 'out_refund':
    #             continue
    #
    #         original = refund.reversed_entry_id
    #         if not original:
    #             continue
    #
    #         # Find commission lines linked to original invoice
    #         settlement_lines = self.env['commission.settlement.line'].search([
    #             ('invoice_id', '=', original.id)
    #         ])
    #
    #         if not settlement_lines:
    #             continue
    #
    #         # We assume lines belong to same settlement (you also have SQL constraints to avoid cross-settlement duplicates)
    #         settlement = settlement_lines[0].settlement_id
    #
    #         total_reclaim = 0.0
    #
    #         for line in settlement_lines:
    #             inv = line.invoice_id
    #
    #             if not inv or inv.amount_total == 0:
    #                 continue
    #
    #             # refund_ratio = refund amount relative to original invoice amount
    #             refund_ratio = abs(refund.amount_total) / inv.amount_total
    #
    #             # reclaimed commission amount from this line
    #             reclaim_amount = (line.invoice_commission or 0.0) * refund_ratio
    #
    #             # accumulate
    #             total_reclaim += reclaim_amount
    #
    #             # update the cumulative refunded commission for this line
    #             # This is stored (not recomputed) so it persists across multiple partial refunds
    #             line.commission_refunded = (line.commission_refunded or 0.0) + reclaim_amount
    #
    #             # if commission fully reclaimed mark as refunded flag (optional)
    #             if (line.commission_refunded or 0.0) >= (line.invoice_commission or 0.0):
    #                 line.is_refunded = True
    #
    #         if total_reclaim <= 0:
    #             continue
    #
    #         # Create vendor credit note for the reseller (value positive)
    #         bill_vals = {
    #             'move_type': 'in_refund',  # Vendor Credit Note
    #             'partner_id': settlement.reseller_id.id,
    #             'invoice_origin': original.name,
    #             'invoice_date': fields.Date.context_today(self),
    #             'invoice_line_ids': [(0, 0, {
    #                 'name': f'Reclaim commission for refund of invoice {original.name}',
    #                 'quantity': 1,
    #                 'price_unit': total_reclaim,  # positive amount for credit note line
    #             })],
    #         }
    #
    #         bill = self.env['account.move'].create(bill_vals)
    #         bill.action_post()
    #
    #         # Update settlement: link to reclaim bill, recompute totals by compute methods
    #         settlement.reclaim_bill_id = bill.id
    #
    #         # If all commission is reclaimed, mark settlement state as reclaimed, else keep accepted
    #         if settlement.total_commission_refunded >= settlement.total_commission:
    #             settlement.state = 'reclaimed'
    #         else:
    #             # keep accepted or set a sub-state if you like
    #             settlement.state = 'accepted'
    #
    #         # Add chatter message
    #         settlement.message_post(
    #             body=f"Vendor refund {bill.name} created for reclaimed commission amount {total_reclaim}."
    #         )
    #
    #     return res
