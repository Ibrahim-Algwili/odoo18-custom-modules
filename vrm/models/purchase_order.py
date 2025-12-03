from odoo import models , api , fields




class PurchaseOrder (models.Model):
    _inherit = 'purchase.order'

    purchase_team_id = fields.Many2one(
        'purchase.team',
        string="Purchase Team"
    )



    @api.onchange('partner_id')
    def _onchange_partner_id_set_team(self):
        if self.partner_id and self.partner_id.purchase_team_id :
            self.purchase_team_id = self.partner_id.purchase_team_id