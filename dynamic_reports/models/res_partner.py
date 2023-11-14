# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class Partner(models.Model):
    _inherit = 'res.partner'

    ar_partner_name = fields.Char(required=False)
    ar_partner_street = fields.Char(required=False)
    customer_department_id = fields.Many2one('hr.department', string="Department", help='Department of the customer')


