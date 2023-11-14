from odoo import models, fields, api, _

class ProductTemplates(models.Model):
    _inherit = "product.template"
 
    is_man_power = fields.Boolean(string="Is Man Power")
    is_man_power_order = fields.Boolean(related="company_id.is_man_power",string="Is Man Power Order Company")





