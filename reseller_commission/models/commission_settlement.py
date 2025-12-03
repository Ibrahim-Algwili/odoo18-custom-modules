import datetime
from datetime import timedelta
from email.policy import default
import logging
_logger = logging.getLogger(__name__)
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CommissionSettlement(models.Model):
    _name = 'commission.settlement'
    _description = 'Commission Settlement'
    _rec_name = 'ref'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # -----------------------------
    # Fields
    # -----------------------------
    active = fields.Boolean(default=True)
    ref = fields.Char(string="Ref" , default='New')

    reseller_id = fields.Many2one(
        'res.partner',
        string="Reseller",
        required=True,
        domain=[('is_reseller', '=', True)]
    )

    period_from = fields.Date(required=1 , default=datetime.datetime.today() - timedelta(days=5))
    period_to = fields.Date(required=1 , default=datetime.datetime.today())

    settlement_line_ids = fields.One2many(
        'commission.settlement.line',
        'settlement_id',
        string="Commission Lines",
    )

    total_commission = fields.Monetary(
        string="Total Commission",
        compute="_compute_total_commission",
        store=True,
        currency_field='currency_id'
    )

    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id.id
    )

    reclaim_bill_id = fields.Many2one(
        'account.move',
        string="Reclaim Vendor Bill",
        readonly=True
    )

    bill_id = fields.Many2one('account.move', string="Vendor Bill")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('accepted', 'Accepted'),
        ('reclaimed', 'Reclaimed'),
    ], default='draft' , tracking=True)

    invoice_ids_used = fields.Many2many(
        'account.move',
        compute = '_compute_invoice_ids_used',
        store=False
    )

    total_commission_refunded = fields.Monetary(
        string="Total Commission Refunded",
        compute='_compute_totals_refunded',
        store=True,
        currency_field='currency_id'
    )

    total_commission_net = fields.Monetary(
        string="Net Total Commission",
        compute='_compute_totals_refunded',
        store=True,
        currency_field='currency_id'
    )

    # @api.depends('settlement_line_ids.commission_refunded', 'total_commission')
    # def _compute_totals_refunded(self):
    #     '''
    #     Compute total refunded commission across settlement lines and net total.
    #     '''
    #     for rec in self:
    #         refunded = sum(rec.settlement_line_ids.mapped('commission_refunded') or [])
    #         rec.total_commission_refunded = refunded
    #         rec.total_commission_net = max((rec.total_commission or 0.0) - refunded, 0.0)

    # -----------------------------
    # Overrides
    # -----------------------------
    @api.model
    def create(self, vals_list):
        ''' Override create to set sequence reference if new '''
        res = super().create(vals_list)
        if res.ref == 'New':
            res.ref = self.env['ir.sequence'].next_by_code('commission.settlement.sequence') or 'New'
        return res

    def unlink(self):
        ''' Prevent deletion if state is not draft '''
        for rec in self:
            if rec.state not in 'draft' :
                raise ValidationError("You Can't Delete in Accepted State")
        super().unlink()

    # -----------------------------
    # Compute Methods
    # -----------------------------
    @api.depends('settlement_line_ids.invoice_commission')
    def _compute_total_commission(self):
        '''
        Compute the total original commission before any refunds.
        '''
        for rec in self:
            rec.total_commission = sum(
                rec.settlement_line_ids.mapped('invoice_commission') or []
            )

    @api.depends('settlement_line_ids.commission_refunded', 'total_commission')
    def _compute_totals_refunded(self):
        '''
        Compute:
        1) total_commission_refunded → sum of refunded commission
        2) total_commission_net → original commission minus refunded
        '''
        for rec in self:
            refunded = sum(
                rec.settlement_line_ids.mapped('commission_refunded') or []
            )
            rec.total_commission_refunded = refunded

            # Net = Original - Refunded
            rec.total_commission_net = max(
                (rec.total_commission or 0.0) - refunded,
                0.0
            )

    @api.depends('settlement_line_ids', 'settlement_line_ids.invoice_id')
    def _compute_invoice_ids_used(self):
        ''' Compute all invoices used in this settlement (to avoid duplicates) '''
        for rec in self:
            rec.invoice_ids_used = rec.settlement_line_ids.mapped('invoice_id')
            _logger.warning('ids used is : %s', rec.invoice_ids_used.ids)

    # -----------------------------
    # Onchange Methods
    # -----------------------------
    @api.onchange('reseller_id')
    def _check_resller(self):
        ''' Clear all commission lines if reseller is changed '''
        if self.settlement_line_ids:
            self.settlement_line_ids = [(5, 0, 0)] # Clear existing lines

    # -----------------------------
    # Actions
    # -----------------------------
    def action_accepted(self):
        '''
        Change the state To Accepted,
        Create Vendor Bill for the commission,
        Raise error if no invoice lines
        '''
        for rec in self:
            if rec.settlement_line_ids:
                rec.state = 'accepted'
                bill_vals = {
                    'move_type' : 'in_invoice' ,      # Vendor Bill
                    'partner_id' : rec.reseller_id.id,
                    'invoice_date' : datetime.datetime.today() ,
                    'currency_id' : rec.currency_id.id ,
                    'invoice_line_ids': [
                        (0, 0, {
                            'name': f"Reseller Commission for invoices: {[inv.name for inv in rec.settlement_line_ids.mapped('invoice_id')] }",
                            'quantity': 1,
                            'price_unit': rec.total_commission,
                        })
                    ]
                }

                # Create and post vendor bill
                bill = rec.env['account.move'].create(bill_vals)
                bill.action_post()
                rec.bill_id = bill.id

                # Post message in chatter
                rec.message_post(body=f"Commission vendor bill {bill.name} created for amount {rec.total_commission}")

            else:
                raise ValidationError("You Can't Put the State on Accepted \n You Have no Invoice Lines")

            # Mark linked invoices as commission accepted
            invoices = rec.mapped('settlement_line_ids.invoice_id')
            invoices.write({'is_commission_accepted' : True})

    def action_pay_commission(self):
        '''
        Open Vendor Bill form view to pay the commission
        '''
        self.ensure_one()
        if not self.bill_id:
            raise ValidationError("No vendor bill linked.")

        return {
            'name' : 'Commission',
            'type' : 'ir.actions.act_window',
            'res_model' : 'account.move',
            'res_id' : self.bill_id.id , # record id
            'view_mode' : 'form',
            'view_id' : self.env.ref('account.view_move_form').id ,
            'target': 'current',
        }

    def action_pay_refund(self):
        '''
        Open Refund Bill form view to reclaim commission from reseller
        '''
        self.ensure_one()
        return {
            'name': 'Commission',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': self.reclaim_bill_id.id,  # record id
            'view_mode': 'form',
            'view_id': self.env.ref('account.view_move_form').id,
            'target': 'current',
        }

    def action_draft(self):
        ''' Change the state To Draft '''
        for rec in self:
            rec.state = 'draft'
