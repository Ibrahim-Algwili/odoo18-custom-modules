from odoo import fields, api, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    purchase_team_ids = fields.Many2many('purchase.team', 'm2m_purchase_team_rel', string='Purchase Teams')
    purchase_team_manager_ids = fields.Many2many('purchase.team', 'm2m_purchase_team_manager_rel',
                                                 string='Managed Purchase Teams')

    def _get_allowed_lead_team_ids(self):
        # هذه الدالة ترجع قائمة IDs الفرق التي يديرها المستخدم
        return self.purchase_team_manager_ids.ids
