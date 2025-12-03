from email.policy import default

from odoo import models, fields, api, exceptions
from odoo.exceptions import UserError


class VrmVendorLead(models.Model):
    _name = "vrm.vendor.lead"
    _description = "VRM Vendor Lead / Pipeline Entry"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "create_date desc"

    name = fields.Char(string="Lead Reference", required=True, tracking=True)
    partner_id = fields.Many2one('res.partner', string="Vendor", ondelete='set null', index=True,
                                 domain="['|' , ('is_vendor' , '=' , True) , ('category_id', 'ilike', 'Vendor')]")
    vrm_stage_id = fields.Many2one('vrm.vendor.stage', string="Stage", tracking=True)
    vrm_tag_ids = fields.Many2many('vrm.vendor.tag', string="Tag", tracking=True)
    expected_annual_spend = fields.Monetary(string="Expected Annual Spend")
    probability = fields.Float(string="Probability (%)", default=0.0, tracking=True)
    currency_id = fields.Many2one('res.currency', string='Currency')
    responsible_id = fields.Many2one('res.users', string="Responsible")
    vrm_tier = fields.Selection([('a', 'Tier A'), ('b', 'Tier B'), ('c', 'Tier C')], string="Tier")
    vrm_risk = fields.Selection([('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], string="Risk Level")
    note = fields.Html(
        'Note', sanitize=True)
    date_next_action = fields.Datetime(string="Next Action Date")
    is_approved = fields.Boolean(string="Approved", default=False, tracking=True)

    achievement_display = fields.Char(
        string='Achievement',
        compute='_compute_achievement_display',
        store=False
    )

    is_won = fields.Boolean(default=False)

    # ----- Vendor Fields -----
    vendor_street = fields.Char('Street')
    vendor_vat = fields.Char('Tax ID')
    vendor_phone = fields.Char('Phone')
    vendor_email = fields.Char('Email')
    vendor_website = fields.Char('Website')
    vendor_country_id = fields.Many2one("res.country", string="Country")
    vendor_purchase_team = fields.Char('Purchase Team')


    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id :
            partner = self.partner_id

            self.vendor_street = partner.street
            self.vendor_vat = partner.vat
            self.vendor_phone = partner.phone
            self.vendor_email = partner.email
            self.vendor_website = partner.website
            self.vendor_country_id = partner.country_id.id
            self.vendor_purchase_team = partner.purchase_team_id.name




    @api.onchange('vrm_stage_id')
    def _onchange_vrm_stage_id(self):
        """ Set probability based on stage change """
        stage_probability_map = {
            'New': 10.0,
            'Evaluation': 40.0,
            'Approved': 60.0,
            'Preferred': 90.0,
            'Won': 100.0,
            'Suspended': 0.0,
        }
        if self.vrm_stage_id and self.vrm_stage_id.name in stage_probability_map:
            self.probability = stage_probability_map[self.vrm_stage_id.name]
        else:
            self.probability = 0.0


    def action_won_lead(self):
        """ Mark the Lead as Won """

        won_stage = self.env['vrm.vendor.stage'].search([('name' , '=' , 'Won')] , limit=1)

        if not won_stage:
            raise UserError('This Stage Not Found!!')

        for lead in self:
            lead.vrm_stage_id = won_stage.id


        lead.message_post(
            body=f"Lead Converted to Won by {self.env.user.name}",
            message_type='notification',
            subtype_xmlid='mail.mt_note'
        )

        self._onchange_vrm_stage_id()

        if won_stage:
            self.is_won = True
        else : self.is_won = False



        return True

    def action_suspend_lead_direct(self):
        """ Suspends the selected vendor leads directly and posts a note in the Chatter. """

        # 1. Search for the target stage (Suspended)
        # We search the stage model for a record named 'Suspended'.
        suspended_stage = self.env['vrm.vendor.stage'].search([('name', '=', 'Suspended')], limit=1)

        # If the stage is not found, raise a user-friendly error.
        if not suspended_stage:
            raise exceptions.UserError(
                "The 'Suspended' stage was not found in the system. Please configure the stage.")

        # 2. Iterate over the selected records (self)
        for lead in self:
            # A. Update the stage field
            lead.vrm_stage_id = suspended_stage.id

            # B. Post a simple notification in the Chatter
            # Using message_post is the standard way to add messages to the activity log.
            lead.message_post(
                body=f"Lead directly moved to **Suspended** stage by {self.env.user.name}.",
                message_type='notification',
                subtype_xmlid='mail.mt_note'
            )

        # Returning True signals Odoo that the server action was executed successfully.
        return True


    def action_rfq(self):
        return {
            'name' : 'New RFQ',
            'type' : 'ir.actions.act_window',
            'view_mode' : 'form',
            'res_model' : 'purchase.order',
            'context' : {
                'default_partner_id': self.partner_id.id,
            } ,
            'target' : 'current'
        }


    def is_state_won(self):
        won_stage = self.env['vrm.vendor.stage'].search([('name', '=', 'Won')], limit=1)

        for rec in self:
            if won_stage:
                rec.is_won = True
            else : rec.is_won = False
