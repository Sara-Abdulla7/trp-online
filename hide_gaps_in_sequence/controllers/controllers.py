# -*- coding: utf-8 -*-
# from odoo import http


# class HideGapsInSequence(http.Controller):
#     @http.route('/hide_gaps_in_sequence/hide_gaps_in_sequence', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hide_gaps_in_sequence/hide_gaps_in_sequence/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('hide_gaps_in_sequence.listing', {
#             'root': '/hide_gaps_in_sequence/hide_gaps_in_sequence',
#             'objects': http.request.env['hide_gaps_in_sequence.hide_gaps_in_sequence'].search([]),
#         })

#     @http.route('/hide_gaps_in_sequence/hide_gaps_in_sequence/objects/<model("hide_gaps_in_sequence.hide_gaps_in_sequence"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hide_gaps_in_sequence.object', {
#             'object': obj
#         })
