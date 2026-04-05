from odoo import _, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    """Extend sale.order to validate product quantities before confirmation.

    The implementation follows a divide-and-conquer approach:
    - _line_needs_check: small helper that checks a single order line
    - _insufficient_lines: collects problematic lines for one order
    - _format_insufficient_message: turns the problem set into a readable message
    - action_confirm: orchestrates checks before calling super()
    """

    _inherit = "sale.order"

    def _line_needs_check(self, line):
        """Return (product, needed_qty, available_qty) when stock is insufficient for the line.
        Skip service products and lines with non-positive quantity.
        Uses product.virtual_available (forecasted availability) to be conservative.
        """
        product = line.product_id
        needed = line.product_uom_qty
        if not product or needed <= 0:
            return None
        # Ignore services
        if product.type == "service":
            return None
        available = product.virtual_available
        if available < needed:
            return (product, needed, available)
        return None

    def _insufficient_lines(self):
        """Return a list of tuples for lines that don't have enough stock.
        Operates on a single sale.order record.
        """
        self.ensure_one()
        problems = []
        for line in self.order_line:
            res = self._line_needs_check(line)
            if res:
                problems.append(res)
        return problems

    def _format_insufficient_message(self, insufficient):
        """Format a readable message for the provided insufficient list."""
        rows = []
        for product, needed, available in insufficient:
            rows.append(
                f"{product.display_name}: ordered={needed}, available={available}"
            )
        return "\n".join(rows)

    def action_confirm(self):
        """Override confirmation to ensure stock sufficiency first.

        If any product lacks stock, raise a UserError with details.
        """
        for order in self:
            insufficient = order._insufficient_lines()
            if insufficient:
                msg = order._format_insufficient_message(insufficient)
                raise UserError(
                    _("Not enough stock for the following products:\n%s") % msg
                )
        # Call parent implementation
        return super(SaleOrder, self).action_confirm()
