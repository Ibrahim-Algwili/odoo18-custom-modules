from email.policy import default

from odoo import models , api , fields
from odoo.exceptions import UserError


class AccountMove(models.Model) :
    _inherit = 'account.move'

    reseller_id = fields.Many2one('res.partner', string="Reseller")
    is_commission_accepted= fields.Boolean(default=False)
    commission_ready = fields.Boolean(
        compute="_compute_commission_paid",
        default=False,
        store=True,
        help="This invoice is fully paid and ready to be used in commission settlements."
    )
    is_refunded = fields.Boolean(string="Is Refunded", default=False)


    @api.depends('payment_state')
    def _compute_commission_paid(self):
        '''
        Make commission_ready = True
        if payment_state is paid
        Benefit : We don't Get any Invoices in Commissions App That is Not Paid
        '''
        for invoice in self:
            invoice.commission_ready = (invoice.state == 'posted' and invoice.payment_state == 'paid')


    def button_cancel(self):
        '''
        Override cancel button to revert any linked commission settlements
        make the settlement draft state before canceling.
        make the invoices available for commission selection again.
        '''
        res = super().button_cancel()

        for move in self:
            settlement = self.env['commission.settlement'].search([('bill_id', '=', move.id)], limit=1)
            if settlement:
                # إعادة فتح العمولة
                settlement.state = 'draft'
                settlement.bill_id = False

                # إعادة الفواتير لتكون قابلة للاختيار من جديد
                settlement.settlement_line_ids.invoice_id.write({'is_commission_accepted': False})

        return res


    def unlink(self):
        '''
        Override unlink to revert any linked commission settlements
        make the settlement draft state before deletion.
        make the invoices available for commission selection again.
        '''
        for move in self:
            settlement = self.env['commission.settlement'].search([('bill_id', '=', move.id)], limit=1)
            if settlement:
                settlement.state = 'draft'
                settlement.bill_id = False
                settlement.settlement_line_ids.invoice_id.write({'is_commission_accepted': False})

        return super().unlink()



    def action_post(self):
        '''Extend posting behavior: when a refund is posted, reclaim reseller commission.'''
        res = super().action_post()

        for refund in self:
            # Only handle customer credit notes
            if refund.move_type != 'out_refund':
                continue

            original = refund.reversed_entry_id
            if not original:
                continue

            # find commission lines linked to the original invoice
            settlement_lines = self.env['commission.settlement.line'].search([
                ('invoice_id', '=', original.id)
            ])
            if not settlement_lines:
                continue

            settlement = settlement_lines[0].settlement_id

            # refund ratio
            if original.amount_total == 0:
                continue

            refund_ratio = abs(refund.amount_total) / original.amount_total
            total_reclaim = 0.0

            for line in settlement_lines:
                commission_original = line.invoice_commission or 0.0

                reclaim_amount = commission_original * refund_ratio
                total_reclaim += reclaim_amount

                # update refunded amount with cap
                new_refunded = line.commission_refunded + reclaim_amount

                # prevent over-refund
                if new_refunded > commission_original:
                    new_refunded = commission_original

                line.commission_refunded = new_refunded

                # if fully refunded, flag it
                if line.commission_refunded >= commission_original:
                    line.is_refunded = True


            if total_reclaim > 0:
                bill_vals = {
                    'move_type': 'in_refund',
                    'partner_id': settlement.reseller_id.id,
                    'invoice_origin': original.name,
                    'invoice_date': fields.Date.context_today(self),
                    'invoice_line_ids': [(0, 0, {
                        'name': f'Reclaimed commission for refund {refund.name}',
                        'quantity': 1,
                        'price_unit': total_reclaim,
                    })],
                }

                bill = self.env['account.move'].create(bill_vals)
                bill.action_post()

                settlement.reclaim_bill_id = bill.id

                # update settlement state
                if settlement.total_commission_refunded >= settlement.total_commission:
                    settlement.state = 'reclaimed'
                else:
                    settlement.state = 'accepted'

                settlement.message_post(
                    body=f"Commission reclaim created because of refund {refund.name}: {total_reclaim}"
                )

        return res




    def _cron_update_commission_ready(self):
        '''
        Stopped for Now!!!
        Search for paid Invoices
        Make the commission_ready field as True to show them in Commission Module
        '''
        # invoices = self.search([
        #     ('move_type', '=', 'out_invoice'),
        #     ('state', '=', 'posted'),
        #     ('commission_ready', '=', False),
        #     ('payment_state', '=', 'paid')
        # ])
        #
        # invoices.write({'commission_ready': True})




