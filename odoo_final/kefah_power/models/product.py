from odoo import models, fields, api, _

class ProductTemplates(models.Model):
    _inherit = "product.template"
 
    is_man_power = fields.Boolean(string="Is Man Power")  
    is_man_power_order = fields.Boolean(related="company_id.is_man_power",string="Is Man Power Order Company")
  
    is_ot = fields.Boolean(string="Is OT")

    ot_ref = fields.Many2one("product.product",string='OT Refrence',domain=[('is_ot', '=', True)])
    ot_price = fields.Float(string='OT Price')

    # ot_ref_id = fields.One2many('project.template','ot_ref',string='OT Refrence')





