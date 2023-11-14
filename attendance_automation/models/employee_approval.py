from odoo import models, fields,api,_
class Employee_approval(models.Model):
    _inherit = "hr.employee"

    type_of_employee = fields.Selection(selection=[('full_time','Full Time'),('out source','Out Sourse')],string="attendance type",default='full_time',required=True)
    attendance_approval = fields.Boolean(string='Attendance Approval',default=True)

    delay_monthly_counter = fields.Integer(string='Late Counter Per Month' , readonly=True)
    absent_monthly_counter = fields.Integer(string='Absent Counter Per Month' , readonly=True)
    # attendance_dup = fields.Boolean(string='Tendance Duplicates')

    # def _compute_time(self):
    #     for rec in self:
    #         if rec.overtime:
    #             rec.datetime.strftime(self.overtime,"%H:%M:%S")



    # api.onchange('check_in')



































