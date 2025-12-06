from odoo import models , api , fields



class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_vendor = fields.Boolean(string='Is Vendor?', help='Indicates whether the partner is a vendor.')

    # vrm_tier = fields.Selection([
    #     ('tier_1', 'Tier A'),
    #     ('tier_2', 'Tier B'),
    #     ('tier_3', 'Tier C'),
    #     ('tier_4', 'Tier D'),
    # ], string='Vendor Tier', help='Tier classification of the vendor based on predefined criteria.')
    #
    # vrm_risk = fields.Selection([
    #     ('low', 'Low Risk'),
    #     ('medium', 'Medium Risk'),
    #     ('high', 'High Risk'),
    # ], string='Vendor Risk Level', help='Risk level associated with the vendor.')
    #
    # vrm_notes = fields.Text(string='Vendor Notes', help='Additional notes or comments about the vendor.')
    # vrm_approval_date = fields.Date(string='Vendor Approval Date', help='Date when the vendor was approved.')
    #
    # vrm_stage_id = fields.Many2one('vrm.vendor.stage', string='Vendor Stage', help='Stage of the vendor in the vendor management process.')



    purchase_team_id = fields.Many2one('purchase.team',string="Purchase Team",help="Which purchase team manages this vendor?")