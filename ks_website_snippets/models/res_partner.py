from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_web_customer = fields.Boolean(string='Is Web Customer')
    is_supplier = fields.Boolean()
    is_partner = fields.Boolean()
