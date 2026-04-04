from odoo import fields, models


class PropertyType(models.Model):
    _name = "property.type"

    name = fields.Char(required=1)
    property_ids = fields.One2many("property", "property_type_id")

    _sql_constraints = [("Unique_Name", "unique(name)", "This Name is Exist")]


    def sql_crud_query(self, qry):
        self.env.cr.execute(qry)
        self.env.cr.commit()
        return True