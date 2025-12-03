from odoo import models , api , fields



class VrmStage(models.Model):
    _name = 'vrm.vendor.stage'
    _description = 'VRM Vendor Stages'
    _rec_name = 'name'
    _order = 'sequence, name, id'


    name = fields.Char('Stage Name', required=True, translate=True)
    sequence = fields.Integer('Sequence', default=1, help="Used to order stages. Lower is better.")
    folded = fields.Boolean('Folded in Pipeline?', default=False)
    color = fields.Integer("Color Index")
