from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    attendance = fields.Boolean(config_parameter=
                                'ks_website_snippets.attendance')
    task = fields.Boolean(config_parameter='ks_website_snippets.task')
