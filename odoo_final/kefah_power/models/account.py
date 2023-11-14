
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class AccountMove(models.Model):
    _inherit = 'account.move'

    is_man_power_order = fields.Boolean(related="company_id.is_man_power" ,string="Is Man Power Order", required=False)
    start_date = fields.Date(string="Start TimeSheet")
    end_date = fields.Date(string="End TimeSheet")
    sale_orders_id = fields.Many2one('sale.order',string='Sale Order') 
    department_sheet = fields.Many2one('department.line.keffah',string="Department" , readonly=True)
    department_arabic = fields.Char(string="Arabic Department Name" ,readonly=True)

    The_number_of_working_days = fields.Integer(string="The Number Of Working Days",readonly=True) 

    total_hours = fields.Integer(readonly="True")
    hours = fields.Integer(compute='hour_compute',readonly=True ,string='Total Hours')

    number_employees = fields.Integer(String="Number Of Employees")

    def hour_compute(self):
        for rec in self.invoice_line_ids:
            self.hours += rec.quantity
        self.total_hours = self.hours
