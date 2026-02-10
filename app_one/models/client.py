from email.policy import default

from odoo import api, fields, models
from odoo.exceptions import ValidationError

"""
this model will create a table copied (inherted) from owner model
"""


class Client(models.Model):
    _name = "client"
    _inherit = "owner"
