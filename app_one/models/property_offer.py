import datetime
from email.policy import default
from odoo.exceptions import RedirectWarning
from odoo import api, fields, models
from odoo.tools import SQL


class PropertyOffer(models.Model):
    _name = "property.offer"
    _rec_name = "partner_id"

    active = fields.Boolean(default=True)
    price = fields.Float()
    status = fields.Selection(
        [
            ("accepted", "Accepted"),
            ("refused", "Refused"),
        ],
        copy="0",
        default=None,
        readonly=1,
    )
    validity = fields.Integer(default=7)

    # Relations
    partner_id = fields.Many2one("res.partner", required=1)
    property_id = fields.Many2one("property", required=1)

    date_deadline = fields.Datetime(
        compute="_compute_date_deadline", readonly=False, default=False
    )

    @api.depends("create_date")
    def _compute_date_deadline(self):
        for rec in self:
            rec.date_deadline = rec.create_date + datetime.timedelta(days=7)

    def _set_date_deadline(self):
        pass

    def archive_records(self):
        for rec in self:
            if rec.id in [1, 2]:
                rec.action_archive()  # important

    def unarchive_records(self):
        for rec in self:
            if rec.id in [1, 2]:
                rec.action_unarchive()  # important

    # Offer Actions
    def action_accept(self, field="status"):
        for rec in self:
            print(rec)
            print(type(rec))
            # rec['status'] = "accepted"
            rec[field] = "accepted"

    def action_refuse(self):
        for rec in self:
            rec.status = "refused"

    @api.onchange("partner_id")
    def _onchange_partner(self):
        message = "Dear %s" % (self.partner_id.name or "")

        return {
            "warning": {"title": "Warning", "message": message, "type": "notification"},
        }

    # ============ env ===============
    def example(self):
        Partner = self.env['res.partner']

        partners = Partner.search([('customer', '=', True)])

        if self.env.is_admin():
            partners = partners.sudo()

        partners = partners.with_context(show_address=True)

        company = self.env.company

        group = self.env.ref('base.group_system')

        return partners


    # ============= Sql =============
    def cr_sql_test(self):
        self.env.flush_all()
        sql = SQL("UPDATE property_offer SET price = %s", 50.0)
        self.env.cr.execute(sql)


    # ============ ORM ==============
    def write(self, vals):
        res = super().write(vals)
        print("Vals : " , vals)
        print("Res" , res)
        if vals.get("price"):
            print("Price Updated Successfully!!")

        return res


    def read(self, fields=None, load=None):
        res = super().read(fields=fields, load=load)
        print("Self : ", self)
        print("Fields : ", fields)
        print("Res : ", res)

        return res

    def search_button(self):
        records = self.search([])
        print("Search : ", records)

        records = self.browse([2,3])
        data = records.read(['price', 'status'])
        print("Read Data: ", data)

    def filter_button(self):
        records = self.search([]).filtered(lambda r: r.price > 50)
        print("Filtered : ", records)

        # return just partner that is a company
        records = self.search([]).filtered("partner_id.is_company")
        print("Filtered : ", records)

    def mapped_button(self):
        records = self.mapped(lambda r: r.price + 5)
        print("Mapped : ", records)

        records = self.search([]).mapped("price")
        print("Mapped : ", records)

        records = self.mapped("partner_id")
        print("Mapped : ", records)

    def grouped_button(self):
        '''
        :return: Dictionary of Record Sets
        '''
        orders = self.env['sale.order'].search([])

        records_grouped = orders.grouped('partner_id')
        print("Grouped : ", records_grouped)

        records_grouped = orders.grouped(lambda o: o.amount_total > 100) # Grouped :  {True: sale.order(24, 23, 22, 21, 16, 14, 13, 12, 18)}
        print("Grouped : ", records_grouped)



    # =========== Warning & Error Messages ============
    def redirect_warning_message(self):
        user = self.env.user

        if user.company_id:
            action = self.env.ref("base.action_res_company_form").id
            raise RedirectWarning(
                    "This User Has No Company",
                    action,
                    "Go To Companies List"
            )


    # ========================== XML-RPC CALL =========================

    def custome_metod_rpc_call(self):
        data = []

        property_details = self.env['property'].search_read([])
        offer_details = self.search_read([])

        data.append({
            "Property Details": property_details,
            "Offer Details": offer_details
        })
        print("Data : --> ", data)

        # self.sql_select_query("SELECT * FROM property_offer")

        return data

    def sql_select_query(self, qry):
        self.env.cr.execute(qry)
        data = self.env.cr.fetchall()
        print("Data From SQL : ", data)
        return data







