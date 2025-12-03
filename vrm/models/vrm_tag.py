from odoo import models , api , fields



class VrmTag(models.Model):
    _name = 'vrm.vendor.tag'
    _description = 'VRM Vendor Tags'
    _rec_name = 'name'
    _order = 'sequence, name, id'


    name = fields.Char('Tag Name', required=True, translate=True)
    sequence = fields.Integer('Sequence', default=1)
    color = fields.Integer('Color Index')
