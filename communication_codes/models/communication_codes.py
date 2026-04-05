# -*- coding: utf-8 -*-

import re

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv import expression


class CommunicationCodes(models.Model):
    _name = "communication.codes"
    _description = _("Communication Codes Management")
    _order = "create_date desc"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    CODE_NUMBER_PATTERN = re.compile(r"^\d{3}-\d{3}-\d{4}$")

    name = fields.Char(
        string=_("Sequence Number"),
        readonly=True,
        copy=False,
        tracking=True,
    )

    employee_id = fields.Many2one(
        "hr.employee",
        string=_("Employee"),
        tracking=True,
        required=True,
        index=True,
    )

    job_id = fields.Many2one(
        "hr.job",
        string=_("Job Position"),
        related="employee_id.job_id",
        store=True,
        readonly=True,
    )

    company_id = fields.Many2one(
        "res.company",
        string=_("Company"),
        related="employee_id.company_id",
        store=True,
        readonly=True,
        index=True,
    )

    branch_id = fields.Many2one(
        "hr.department",
        string=_("Branch"),
        related="employee_id.department_id",
        store=True,
        readonly=True,
    )

    city = fields.Char(
        string=_("City"),
        tracking=True,
        index=True,
    )

    code_number = fields.Char(
        string=_("Code Number"),
        tracking=True,
        required=True,
        copy=False,
        index=True,
    )

    code_system = fields.Selection(
        selection=[
            ("prepaid", _("Prepaid")),
            ("monthly_invoice", _("Monthly Invoice")),
            ("other", _("Other")),
        ],
        string=_("Code System"),
        tracking=True,
        required=True,
        default="prepaid",
        index=True,
    )

    monthly_balance = fields.Float(
        string=_("Monthly Balance"),
        tracking=True,
    )

    code_status = fields.Selection(
        selection=[
            ("in_stock", _("In Stock")),
            ("delivered", _("Delivered")),
            ("suspended", _("Suspended")),
            ("cancelled", _("Cancelled")),
        ],
        string=_("Code Status"),
        tracking=True,
        required=True,
        default="in_stock",
        index=True,
    )

    code_version = fields.Selection(
        selection=[
            ("original", _("Original")),
            ("new_version", _("New Version")),
        ],
        string=_("Code Version"),
        tracking=True,
        default="original",
    )

    version_note = fields.Text(
        string=_("Version Note"),
        tracking=True,
    )

    delivery_date = fields.Datetime(
        string=_("Delivery Date"),
        tracking=True,
    )

    delivery_user_id = fields.Many2one(
        "res.users",
        string=_("Delivered By"),
        tracking=True,
    )

    notes = fields.Html(
        string=_("Notes"),
        sanitize=True,
        sanitize_tags=True,
    )

    active = fields.Boolean(
        string=_("Active"),
        default=True,
        tracking=True,
        index=True,
    )

    _sql_constraints = [
        (
            "unique_code_number",
            "unique(code_number)",
            _("Code number already exists. Please use a different number."),
        ),
    ]

    @api.constrains("code_number")
    def _validate_code_number(self):
        for record in self:
            if not record.code_number:
                raise ValidationError(_("Code number is required."))
            code = record.code_number.strip()
            if not self.CODE_NUMBER_PATTERN.match(code):
                raise ValidationError(
                    _("Code number must be in format: XXX-XXX-XXXX\n")
                    + _("Example: 091-123-4567")
                )

    @api.constrains("monthly_balance")
    def _validate_monthly_balance(self):
        for record in self:
            if record.monthly_balance and record.monthly_balance < 0:
                raise ValidationError(_("Monthly balance cannot be negative."))

    @api.constrains("code_status", "delivery_date", "delivery_user_id")
    def _validate_delivery_fields(self):
        for record in self:
            if record.code_status == "delivered":
                if not record.delivery_date or not record.delivery_user_id:
                    raise ValidationError(
                        _(
                            "Delivery date and delivered by user are required when status is Delivered."
                        )
                    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("name"):
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("communication.codes")
                    or "SIM-00001"
                )
        return super().create(vals_list)

    def write(self, vals):
        if "code_number" in vals:
            for record in self:
                if vals["code_number"] != record.code_number:
                    vals["code_version"] = "new_version"
        return super().write(vals)

    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {})
        default.update(
            {
                "code_number": "091-000-0000",
                "code_status": "in_stock",
                "delivery_date": False,
                "delivery_user_id": False,
            }
        )
        message = _("Please change the phone number")
        self._notify_user(message)
        return super().copy(default)

    def _notify_user(self, message):
        user = self.env.user
        self.env["bus.bus"]._sendone(
            user.partner_id,
            "simple_notification",
            {
                "title": _("Notification"),
                "message": message,
                "type": "warning",
                "sticky": False,
            },
        )

    def action_create_new_version(self):
        self.ensure_one()
        return {
            "name": _("Create New Version"),
            "type": "ir.actions.act_window",
            "res_model": "communication.codes",
            "view_mode": "form",
            "context": {
                "default_employee_id": self.employee_id.id,
                "default_code_version": "new_version",
                "default_version_note": f'{_("New version for original code")}: {self.code_number}',
            },
        }

    def action_deliver(self):
        self.ensure_one()
        self.write(
            {
                "code_status": "delivered",
                "delivery_date": fields.Datetime.now(),
                "delivery_user_id": self.env.user.id,
            }
        )

    def action_suspend(self):
        self.ensure_one()
        self.write({"code_status": "suspended"})

    def action_cancel(self):
        self.ensure_one()
        self.write({"code_status": "cancelled"})

    def action_return_to_stock(self):
        self.ensure_one()
        self.write(
            {
                "code_status": "in_stock",
                "delivery_date": False,
                "delivery_user_id": False,
            }
        )

    def action_employee_codes(self):
        self.ensure_one()
        return {
            "name": _("Employee Codes"),
            "type": "ir.actions.act_window",
            "res_model": "communication.codes",
            "view_mode": "list,form",
            "domain": [("employee_id", "=", self.employee_id.id)],
            "context": {"create": False},
            "target": "current",
        }

    def action_export_excel(self):
        return {
            "name": _("Export to Excel"),
            "type": "ir.actions.act_window",
            "res_model": "export.communication.codes.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_code_ids": [(6, 0, self.ids)]},
        }

    @api.model
    def _name_search(self, name, domain=None, operator="ilike", limit=None, order=None):
        domain = domain or []
        if name:
            name_domain = [
                "|",
                ("code_number", operator, name),
                ("employee_id.name", operator, name),
            ]
            domain = expression.AND([name_domain, domain])
        return self._search(domain, limit=limit, order=order)

    @api.model
    def get_dashboard_stats(self):
        domain = [("company_id", "in", self.env.companies.ids)]

        status_data = self.read_group(domain, ["code_status"], ["code_status"])
        status_counts = {"in_stock": 0, "delivered": 0, "suspended": 0, "cancelled": 0}
        total_count = 0
        for data in status_data:
            count = data.get("code_status_count") or 0
            status = data.get("code_status")
            if status in status_counts:
                status_counts[status] = count
                total_count += count

        system_data = self.read_group(domain, ["code_system"], ["code_system"])
        system_counts = {"prepaid": 0, "monthly_invoice": 0, "other": 0}
        for data in system_data:
            count = data.get("code_system_count") or 0
            system = data.get("code_system")
            if system in system_counts:
                system_counts[system] = count

        balance_data = self.read_group(domain, ["monthly_balance:sum"], [])
        total_balance = balance_data[0].get("monthly_balance") if balance_data else 0

        company_group = self.read_group(
            domain,
            ["company_id"],
            ["company_id"],
            limit=5,
            orderby="company_id_count desc",
        )
        company_stats = []
        for comp in company_group:
            count = comp.get("company_id_count") or 0
            company_name = (
                comp.get("company_id")[1] if comp.get("company_id") else _("Unknown")
            )
            company_stats.append(
                {
                    "name": company_name,
                    "count": count,
                    "percent": (count / total_count * 100) if total_count > 0 else 0,
                }
            )

        recent_codes = self.search(domain, limit=5, order="create_date desc")
        color_map = {
            "in_stock": "success",
            "delivered": "info",
            "suspended": "warning",
            "cancelled": "danger",
        }
        status_selection = dict(self._fields["code_status"].selection)

        recent_data = []
        for rec in recent_codes:
            recent_data.append(
                {
                    "id": rec.id,
                    "code_number": rec.code_number or rec.name,
                    "employee_name": rec.employee_id.name or _("No Employee"),
                    "status_name": status_selection.get(rec.code_status, ""),
                    "status_color": color_map.get(rec.code_status, "secondary"),
                    "company_name": rec.company_id.name if rec.company_id else "",
                }
            )

        return {
            "total_count": total_count,
            "status_counts": status_counts,
            "system_counts": system_counts,
            "total_balance": total_balance,
            "company_count": len(company_group),
            "company_stats": company_stats,
            "recent_codes": recent_data,
        }
