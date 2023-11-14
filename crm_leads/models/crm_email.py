from odoo import models, fields


class CrmEmail(models.Model):
    _name = 'crm.email'
    _description = "CRM Email"

    employee_id = fields.Many2one('hr.employee', string=' Employee Name')
    work_email = fields.Char(related='employee_id.work_email', string='Work Email')
    email_type = fields.Selection([('to', 'To'), ('cc', 'Cc')], string="Send Type")
