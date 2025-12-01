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



    # def action_commissions(self):
    #     self.ensure_one()
    #
    #     if not self.commission_bill_id:
    #         raise UserError("لا توجد فاتورة عمولة مرتبطة بهذه الفاتورة.")
    #
    #     return {
    #         'name': 'Commission Bill',
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'account.move',
    #         'res_id': self.commission_bill_id,
    #         'view_mode': 'form',
    #         'view_id': self.env.ref('account.view_move_form').id,
    #         'target': 'current',
    #     }


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




