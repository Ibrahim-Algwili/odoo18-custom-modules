from odoo import models, fields, api


class PurchaseTeam(models.Model):
    _name = 'purchase.team'
    _description = "Purchase Team"

    name = fields.Char("Team Name", required=True)
    manager_id = fields.Many2one('res.users', string="Team Manager" , required=1)

    user_ids = fields.Many2many(
        'res.users',
        'purchase_team_user_rel',   # ✅ اسم جدول الربط
        'team_id',                  # ✅ عمود الفريق
        'user_id',                  # ✅ عمود المستخدم
        string="Team Members"
    )

