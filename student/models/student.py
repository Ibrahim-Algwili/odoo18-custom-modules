# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger("Hemo Custom LOGGER")


# Difference between (_name , _table)
class DummyStudent(models.Model):
    _name = "dummy.student"  # always use this name
    _table = "my_dummy_students"  # this is just in postgres
    _description = "Dummy Student"


class student(models.Model):
    _name = "student.student"
    _description = "student.student"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    active = fields.Boolean(default=True)
    name = fields.Char()
    age = fields.Integer(default=None)
    dob = fields.Date()
    description = fields.Text()
    is_bool = fields.Boolean(default=True)
    image = fields.Image()

    def action_seach_fetch(self):
        # seach_fetch method
        # search_fetch(domain,field_list,offset,limit.order)
        # Returns Record Set
        print(self)

        stud_obj = self.search_fetch([], [])
        for stud in stud_obj:
            print("name is :", stud.name)

    # print report
    def print_report(self):
        return self.env.ref(
            "custom_header_footer_pdf.student_report_template"
        ).report_action(self)

    def action_log(self):
        _logger.info("Custom Info Log")
        _logger.debug(
            "Custom Debug Log , needs (--log-level=debug) to appear on the log"
        )
        _logger.error("Custom Error Log")
        _logger.critical("Custom Critical Log")
        _logger.warning("Custom Warning Log")

    # Notificaion
    def popup(self):
        message = f"this is from {self.name}."
        self.env["bus.bus"]._sendone(
            self.env.user.partner_id,  # the partner you want the notificatin appear to
            "simple_notification",
            {
                "title": "Warning",
                "message": message,
                "sticky": False,  # if True the message won't remove from the screen
                "warning": True,
            },
        )

    def write(self, values):
        res = super(student, self).write(values)
        self.env["bus.bus"]._sendone(
            self.env.user.partner_id,
            "simple_notification",
            {
                "title": "Info",
                "message": f"{values} successfully updated.",
            },
        )
        return res
