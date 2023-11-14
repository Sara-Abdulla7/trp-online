from odoo import models, fields,api,_
from datetime import date
from odoo.exceptions import UserError, ValidationError


class HrAttendanceOvertime(models.Model):
    _name = "attendance.auto"

    attend_type = fields.Selection(selection=[('absent','Absent'),('holiday','In Holiday'),('excuse','An Excuse'),('attend','Attend'),('late','Late')],string="attendance type")
    delay_time = fields.Float(string='Delay Time',default=8.50)
    absent_time = fields.Float(string='Absent Time',default=10.00)
    check_in = fields.Datetime(string="Check-In")

    absent_check = fields.Boolean(string='Absent Check')
    delay_check = fields.Boolean(string='Delay Check')

    employee_id = fields.Many2one('hr.employee',string="Employee")
    department_id = fields.Many2one('hr.department',string="Department")



    # @api.depends('check_out')
    # def _check_out_today(self):
    #     for record in self:
    #         if record.check_out:
    #             record.overtime = date.today()

    # @api.depends('check_out')
    # def _check_duplicates_employee(self):
    #     for record in self:
    #         lis = []
    #         emp_id = self.env['hr.attendance'].sudo().search([('employee_id','=',record.employee_id.id),('overtime','=',date.today())])
    #         for rec in emp_id:
    #             lis.append(rec)
    #             if len(lis) > 1:
    #                 for obj in lis:
    #                     data = self.env['hr.attendance'].search([('id','=',obj.id)]).write({'attendance_dup':True})
    #             else:
    #                 record.attendance_dup = False



