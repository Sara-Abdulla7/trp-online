from odoo import models, fields,api,_
from datetime import date,datetime
from odoo.exceptions import UserError, ValidationError


class Employee_allow_delay_time(models.Model):


    _name = "attendance.settings"


    # delay_time_check = fields.Boolean(string="Allow Delay Attendance warning")


    delay_time = fields.Float(string='Delay Time',default=8.50)
    absent_time = fields.Float(string='Absent Time',default=10.00)

    employee_id = fields.Many2one('hr.employee',string="Employee")
    department_id = fields.Many2one('hr.department',string="Department")
    mode = fields.Selection(selection=[('employee',' By Employee'),('department',' By Department')],default="employee",required=True)


    # department_check = fields.Boolean(string="By Department")

    # employee_check = fields.Boolean(string="By Employee")

    # def set_values(self):
       
    @api.onchange('mode')
    def change_mode(self):
        if self.mode == 'department':
            self.employee_id = False
        else:
            self.department_id = False