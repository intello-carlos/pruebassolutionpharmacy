# -*- coding: utf-8 -*-
# from odoo import http


# class Quotator(http.Controller):
#     @http.route('/quotator/quotator/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/quotator/quotator/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('quotator.listing', {
#             'root': '/quotator/quotator',
#             'objects': http.request.env['quotator.quotator'].search([]),
#         })

#     @http.route('/quotator/quotator/objects/<model("quotator.quotator"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('quotator.object', {
#             'object': obj
#         })
