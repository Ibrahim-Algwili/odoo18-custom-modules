from odoo import models, fields, api



class ResPartner(models.Model):
    _inherit = 'res.partner'


    def action_open_whatsapp_wizard(self):
        return {
            "type": "ir.actions.act_window",
            "name": "WhatsApp Message Send",
            "res_model": "whatsapp.send.message",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_mobile_number": self.mobile or self.phone,
                "default_message": f"Hello {self.name}, "
            }
        }