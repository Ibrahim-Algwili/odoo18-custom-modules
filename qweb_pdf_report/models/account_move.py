from odoo import models, fields, api
from num2words import num2words

class AccountMove(models.Model):
    _inherit = "account.move"


    def get_amount_inwords(self):
        self.ensure_one()
        units_name = self.currency_id.currency_unit_label or ''
        return num2words(self.amount_total, lang='ar') + ' ' + units_name