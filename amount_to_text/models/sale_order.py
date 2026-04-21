from odoo import fields, api, models
import num2words


class SaleOrder(models.Model):
    _inherit = 'sale.order'


    amount_to_text = fields.Char(string='Amount in Text', compute='_compute_amount_to_text')


    def _compute_amount_to_text(self):
        """ Converting Amount to Text Based on Currency """
        for order in self:
            order.amount_to_text = order.currency_id.amount_to_text(order.amount_total)