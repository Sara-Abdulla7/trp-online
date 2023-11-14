from odoo import models, fields, api


class Product_template(models.Model):
	_inherit='product.template'

	arabic_name = fields.Char(string="Product Name In Arabic", required=True)
