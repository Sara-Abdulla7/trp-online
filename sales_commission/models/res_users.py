from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResUsers(models.Model):
    _inherit = 'res.users'

    is_salesperson = fields.Boolean()

    @api.constrains('is_salesperson')
    def check_salesperson_is_employee(self):
        check = self.env['hr.employee'].search([('user_id', '=', self.id)], limit=1)
        if not check:
            raise ValidationError(_('Please create employee for this user before it salesperson'))
