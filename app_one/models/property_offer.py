import datetime
from email.policy import default

from odoo import api, fields, models


class PropertyOffer(models.Model):
    _name = "property.offer"

    active = fields.Boolean(default=True)
    price = fields.Float()
    status = fields.Selection(
        [
            ("accepted", "Accepted"),
            ("refused", "Refused"),
        ],
        copy="0",
        default=None,
        readonly=1,
    )
    validity = fields.Integer(default=7)

    # Relations
    partner_id = fields.Many2one("res.partner", required=1)
    property_id = fields.Many2one("property", required=1)

    date_deadline = fields.Datetime(compute="_compute_date_deadline", readonly=False , default=False)

    @api.depends("create_date")
    def _compute_date_deadline(self):
        for rec in self:
            rec.date_deadline = rec.create_date + datetime.timedelta(days=7)

    def _set_date_deadline(self):
        pass


    def archive_records(self):
        for rec in self:
            if rec.id in [1,2]:
                rec.action_archive() # important

    def unarchive_records(self):
        for rec in self:
            if rec.id in [1,2]:
                rec.action_unarchive() # important


    # Offer Actions
    def action_accept(self, field='status'):
        for rec in self:
            print(rec)
            print(type(rec))
            # rec['status'] = "accepted"
            rec[field] = "accepted"
    def action_refuse(self):
        for rec in self:
            rec.status = "refused"

    @api.onchange('partner_id')
    def _onchange_partner(self):
        message = "Dear %s" % (self.partner_id.name or "")

        return {
            'warning':
                {
                    'title': "Warning",
                    'message': message,
                    'type': 'notification'
                },
        }
