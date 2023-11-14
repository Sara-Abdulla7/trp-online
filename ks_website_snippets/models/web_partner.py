from odoo import fields, models


class WebPartner(models.Model):
    _name = 'web.partner'
    _description = 'Web Partner'

    name = fields.Char(required=True)
    image_1920 = fields.Binary(required=True)
    description = fields.Text()
