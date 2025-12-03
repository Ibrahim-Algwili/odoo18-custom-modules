from markupsafe import Markup

from odoo import models , api , fields



class SuspendReason(models.TransientModel):
    _name = 'suspend.reason.wizard'
    _description = 'VRM Suspend Reason'

    name = fields.Char('Suspend Reason', required=True, translate=True)
    suspend_feedback = fields.Html(
        'Suspend Note', sanitize=True
    )
    lead_ids = fields.Many2many('vrm.vendor.lead', string='Vendor Leads')


    def action_suspend_reason_apply(self):
        """Mark vendor lead as suspended and apply the suspend reason"""
        self.ensure_one()
        if not self.suspend_feedback:
            self.lead_ids._track_set_log_message(
                Markup('<div style="margin-bottom: 4px;"><p>%s:</p>%s<br /></div>') % (
                    ('Suspend Comment'),
                    self.suspend_feedback
                )
            )
        suspended_stage = self.env['vrm.vendor.stage'].search([('name', '=', 'Suspended')], limit=1)
        for lead in self.lead_ids:
            lead.vrm_stage_id = suspended_stage.id
        #     lead.note = (lead.note or '') + f"\n\nSuspend Reason: {self.name}\n{self.suspend_feedback or ''}"


        return True
