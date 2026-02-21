# -*- coding: utf-8 -*-
# from odoo import http


# class IslamicNotifications(http.Controller):
#     @http.route('/islamic_notifications/islamic_notifications', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/islamic_notifications/islamic_notifications/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('islamic_notifications.listing', {
#             'root': '/islamic_notifications/islamic_notifications',
#             'objects': http.request.env['islamic_notifications.islamic_notifications'].search([]),
#         })

#     @http.route('/islamic_notifications/islamic_notifications/objects/<model("islamic_notifications.islamic_notifications"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('islamic_notifications.object', {
#             'object': obj
#         })

