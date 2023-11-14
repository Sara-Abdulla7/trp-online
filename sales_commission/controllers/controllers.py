# -*- coding: utf-8 -*-
# from odoo import http


# class SalesCommission(http.Controller):
#     @http.route('/sales_commission/sales_commission', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sales_commission/sales_commission/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('sales_commission.listing', {
#             'root': '/sales_commission/sales_commission',
#             'objects': http.request.env['sales_commission.sales_commission'].search([]),
#         })

#     @http.route('/sales_commission/sales_commission/objects/<model("sales_commission.sales_commission"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sales_commission.object', {
#             'object': obj
#         })
