# -*- coding: utf-8 -*-
from odoo import http


class QwebTutorial(http.Controller):
    @http.route("/qweb_tutorial", type="http", auth="public", website=True)
    def qweb_tutorial(self):
        return http.request.render("qweb_tutorial.python_template")
