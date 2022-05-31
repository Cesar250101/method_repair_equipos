# -*- coding: utf-8 -*-
from odoo import http

# class MethodRepairEquipos(http.Controller):
#     @http.route('/method_repair_equipos/method_repair_equipos/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/method_repair_equipos/method_repair_equipos/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('method_repair_equipos.listing', {
#             'root': '/method_repair_equipos/method_repair_equipos',
#             'objects': http.request.env['method_repair_equipos.method_repair_equipos'].search([]),
#         })

#     @http.route('/method_repair_equipos/method_repair_equipos/objects/<model("method_repair_equipos.method_repair_equipos"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('method_repair_equipos.object', {
#             'object': obj
#         })