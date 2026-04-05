import urllib.parse

from odoo import fields, models


class WhatsappSendMessage(models.TransientModel):
    """This model is used for sending WhatsApp messages through Odoo."""

    _name = "whatsapp.send.message"
    _description = "Whatsapp Wizard"

    user_id = fields.Many2one("res.partner", string="Recipient")
    mobile = fields.Char(related="user_id.mobile", required=True)
    message = fields.Text(string="Message", required=True)

    def action_send_message(self):
        """This method is called to send the WhatsApp message using the
        provided details."""
        # Work on a single record and build a properly encoded URL.
        self.ensure_one()
        if self.message and self.mobile:
            # Use urllib.parse to properly URL-encode the message text
            message_string = urllib.parse.quote_plus(self.message)
            # Prefer the related mobile field value (this.mobile is related)
            phone = self.mobile
            return {
                "type": "ir.actions.act_url",
                "url": "https://api.whatsapp.com/send?phone="
                + phone
                + "&text="
                + message_string,
                "target": "new",
                "res_id": self.id,
            }
