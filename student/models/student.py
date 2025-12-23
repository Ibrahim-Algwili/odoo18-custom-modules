# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger("Hemo Custom LOGGER")


# Difference between (_name , _table)
class DummyStudent(models.Model):
    _name = 'dummy.student' # always use this name
    _table = 'my_dummy_students' # this is just in postgres
    _description = 'Dummy Student'



class student(models.Model):
    _name = 'student.student'
    _description = 'student.student'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    name = fields.Char()
    age = fields.Integer(default=None)
    dob = fields.Date()
    description = fields.Text()
    is_bool = fields.Boolean(default=True)



    def action_seach_fetch(self):
        # seach_fetch method
        # search_fetch(domain,field_list,offset,limit.order)
        # Returns Record Set
        print(self)

        stud_obj = self.search_fetch([] , [])
        for stud in stud_obj:
            print("name is :" , stud.name)


    def action_log(self):
        _logger.info("Custom Info Log")
        _logger.debug("Custom Debug Log , needs (--log-level=debug) to appear on the log")
        _logger.error("Custom Error Log")
        _logger.critical("Custom Critical Log")
        _logger.warning("Custom Warning Log")





