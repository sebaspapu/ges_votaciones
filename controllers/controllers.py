# -*- coding: utf-8 -*-
# from odoo import http


# class GesVotaciones(http.Controller):
#     @http.route('/ges_votaciones/ges_votaciones', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ges_votaciones/ges_votaciones/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('ges_votaciones.listing', {
#             'root': '/ges_votaciones/ges_votaciones',
#             'objects': http.request.env['ges_votaciones.ges_votaciones'].search([]),
#         })

#     @http.route('/ges_votaciones/ges_votaciones/objects/<model("ges_votaciones.ges_votaciones"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ges_votaciones.object', {
#             'object': obj
#         })
