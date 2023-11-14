from odoo import models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    is_salesperson = fields.Boolean(string='Is Salesperson')
