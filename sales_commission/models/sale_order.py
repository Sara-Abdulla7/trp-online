from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    commission_done = fields.Boolean(string='Commission Done')
