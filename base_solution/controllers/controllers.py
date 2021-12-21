# -*- coding: utf-8 -*-
# from odoo import http


# class BaseSolution(http.Controller):
#     @http.route('/base_solution/base_solution/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/base_solution/base_solution/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('base_solution.listing', {
#             'root': '/base_solution/base_solution',
#             'objects': http.request.env['base_solution.base_solution'].search([]),
#         })

#     @http.route('/base_solution/base_solution/objects/<model("base_solution.base_solution"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('base_solution.object', {
#             'object': obj
#         })
