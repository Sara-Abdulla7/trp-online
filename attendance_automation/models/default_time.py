from odoo import models, fields,api,_
from datetime import date,datetime
from odoo.exceptions import UserError, ValidationError


class Employee_allow_delay_time(models.Model):


    _name = "attendance.default"


    # delay_time_check = fields.Boolean(string="Allow Delay Attendance warning")


    # delay_time_default = fields.Datetime(string='Delay Time')
    default_delay_time = fields.Float(string='Default Delay Time',default=8.50)
    default_absent_time= fields.Float(string='Default Absent Time',default=10.00)

    # order_ids = fields.One2many('order.line.keffah','project_order_id',string="Order Line")

    default_id = fields.One2many('hr.attendance','default_id',string="Default id")
    # absent_time_default = fields.Datetime(string='Absent Time',default= datetime.now().replace(hour=5, minute=30, second=0))


