from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CommissionSettlementLine(models.Model):
    _name = "commission.settlement.line"
    _description = "Commission Settlement Line"
    _order = "invoice_id"

    settlement_id = fields.Many2one(
        'commission.settlement',
        string="Settlement",
        ondelete='cascade'
    )

    invoice_id = fields.Many2one(
        'account.move',
        string="Invoice",
        required=True,
        domain=[
            ('move_type', '=', 'out_invoice'),
        ],
    )


    invoice_total = fields.Monetary(
        string="Invoice Total",
        currency_field='currency_id',
        compute="_compute_invoice_amounts",
        store=True,
    )

    invoice_commission = fields.Monetary(
        string="Commission Amount",
        currency_field='currency_id',
        compute="_compute_invoice_amounts",
        store=True,
    )

    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id.id
    )

    is_refunded = fields.Boolean(
        string="Refunded",
        compute="_compute_is_refunded",
        store=True
    )

    # ---------------------
    # ---- Constraints ----
    # ---------------------

    # SQL constraint to prevent the same invoice from being added twice to the same settlement
    _sql_constraints = [
        (
            'unique_invoice_per_settlement',  # constraint name
            'unique(settlement_id, invoice_id)',  # uniqueness condition
            'Cannot add the same invoice twice to the same commission settlement!'  # error message
        ),
        (
            'unique_invoices',  # constraint name
            'unique(invoice_id)',  # uniqueness condition
            'This invoice is already added to another settlement!'  # error message
        )
    ]

    @api.constrains('invoice_id')
    def _check_invoice_not_duplicate(self):
        '''
        Constraint method to ensure that the same invoice is not added multiple times
        to the same commission settlement.

        Steps:
        1. For each record being created or updated, check for other records in the
           same settlement with the same invoice.
        2. If a duplicate is found, raise a ValidationError.

        This works even if users try to bypass the SQL constraint (e.g., via API).
        '''
        for rec in self:
            duplicates = self.search([
                ('id', '!=', rec.id),  # exclude the current record
                ('settlement_id', '=', rec.settlement_id.id),  # same commission settlement
                ('invoice_id', '=', rec.invoice_id.id),  # same invoice
            ], limit=1)

            if duplicates:
                raise ValidationError(
                    "This invoice is already added to this settlement!"
                )

    # -----------------------------
    # ------- Functions -----------
    # -----------------------------

    @api.depends(
        'invoice_id',
        'invoice_id.reversed_entry_id',
        'invoice_id.reversed_entry_id.state',
        'invoice_id.reversed_entry_id.move_type'
    )
    def _compute_is_refunded(self):
        '''
        Compute whether the invoice has been refunded.
        True if the invoice has a linked reversed entry that is posted and is an out_refund.
        '''
        for rec in self:
            rec.is_refunded = bool(
                rec.invoice_id.reversed_entry_id and
                rec.invoice_id.reversed_entry_id.state == 'posted' and
                rec.invoice_id.reversed_entry_id.move_type == 'out_refund'
            )

    # The compute method for calculating amounts:
    @api.depends('invoice_id')
    def _compute_invoice_amounts(self):
        '''
        Compute the total invoice amount and the commission for this invoice line.
        Commission is calculated based on product commission rates.
        '''
        for line in self:
            # Check if invoice is linked
            if not line.invoice_id:
                line.invoice_total = 0.0
                line.invoice_commission = 0.0
                continue

            invoice = line.invoice_id

            # 1) Calculate Total Invoice Amount
            line.invoice_total = invoice.amount_total

            # 2) Calculate Commission Amount
            total_commission = 0.0
            for inv_line in invoice.invoice_line_ids:
                product = inv_line.product_id
                # Get commission rate from product (assuming it's defined on product.template)
                rate = product.commision_rate or 0
                subtotal = inv_line.price_subtotal

                total_commission += (subtotal * rate) / 100

            line.invoice_commission = total_commission



