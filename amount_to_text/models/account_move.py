from odoo import fields, api, models
import num2words


class AccountMove(models.Model):
    _inherit = 'account.move'


    amount_to_text = fields.Char(string='Amount in Text', compute='_compute_amount_to_text')


    def _compute_amount_to_text(self):
        """ Converting Amount to Text Based on Currency """
        for inv in self:
            inv.amount_to_text = inv.currency_id.amount_to_text(inv.amount_total)