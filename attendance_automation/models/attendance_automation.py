from odoo import models, fields,api,_
from datetime import date,datetime
from odoo.exceptions import UserError, ValidationError

class HrAttendanceAutomation(models.Model):
    _inherit = "hr.attendance"

    delay_time = fields.Float(string='Delay Time',readonly=True)
    absent_time = fields.Float(string='Absent Time',readonly=True)
    absent_check = fields.Boolean(string='Absent Check')
    delay_check = fields.Boolean(string='Delay Check',)
    attend_type = fields.Selection(selection=[('absent','Absent'),('holiday','In Holiday'),('excuse','An Excuse'),('late','Late'),('attend','Attend'),('already','-')],string="attendance type")

    is_check = fields.Boolean(string='is_check')

    default_id = fields.Many2one('attendance.default',string="Default")


    def attendance_delay_cron(self):


        day = date.today().strftime('%d')

        #Search All employee who didnt got resault yet
        all_employee_attendance = self.env['hr.attendance'].search([('is_check','=',False)])
        if all_employee_attendance:
            for rec in all_employee_attendance:

                rec.is_check= True
                rec.default_id = 1

        #Get default delay and absent time 
                get_delay_by_employee = rec.env['attendance.settings'].search([('employee_id','=',rec.employee_id.id)])
                # rec.delay_time = 
                if get_delay_by_employee:
                    for line in get_delay_by_employee:
                        rec.delay_time = line.delay_time
                        rec.absent_time = line.absent_time
                else:
                    get_delay_by_department = rec.env['attendance.settings'].search([('department_id','=',rec.employee_id.department_id.id)])
                    if get_delay_by_department:
                        for line in get_delay_by_department:
                            rec.delay_time = line.delay_time
                            rec.absent_time= line.absent_time
                    else:
                        rec.delay_time = rec.default_id.default_delay_time
                        rec.absent_time = rec.default_id.default_absent_time



        #check if employee who are delay or absent or not
                check_in_new_day = rec.check_in.strftime('%d')
                all_attendace = rec.env['hr.attendance'].search([('id' ,'!=',rec.id),('employee_id','=',rec.employee_id.id)])
                monthly_counter = 0

                delay_time = float('{0:02.0f}.{1:02.0f}'.format(*divmod(float(rec.delay_time) * 60, 60)))
                absent_time = float('{0:02.0f}.{1:02.0f}'.format(*divmod(float(rec.absent_time) * 60, 60)))
                check_in = float(rec.check_in.strftime('%H.%M'))
                check_in += 3.0
                # delay_time_1= float(delay_time)
                # absent_time_1 = float(ab)

                is_checked = False
                is_check_smaller = False
                if day == check_in_new_day:
                    # min_date_today=0.0
                    if all_attendace:

                        for line in all_attendace:
                            if line:
                                if line.check_in.strftime('%d') == day:
                                    if line.is_check == True:
                                        is_checked = True
                                        break
                    if is_checked == True:
                        rec.attend_type = 'already'
                        continue

                    if all_attendace:
                        for line in all_attendace:
                            if line:
                                if line.check_in.strftime('%d') == day:
                                    if line.check_in < rec.check_in:
                                        is_check_smaller = True
                                        
                    if is_check_smaller == True:
                        rec.attend_type = 'already'
                        continue


                    if absent_time < check_in:
                        rec.absent_check = True

                    elif delay_time < check_in and absent_time > check_in:
                        rec.delay_check = True   

                    if rec.delay_check == True:
                        rec.attend_type = 'late'
                        monthly_counter = monthly_counter + 1
                        month = date.today().strftime('%m')
                        check_in_month = rec.check_in.strftime('%m')
                        if month == check_in_month:
                            if all_attendace:
                                for line in all_attendace:
                                    if line:
                                        if line.check_in.strftime('%m') == month:

                                            if line.delay_check == True:
                                                monthly_counter = monthly_counter + 1
                        rec.employee_id.delay_monthly_counter = monthly_counter
                        
                        valus ={
                            'employee_id':rec.employee_id.id,
                            'department_id':rec.employee_id.department_id.id,
                            'delay_check':rec.delay_check,
                            'delay_time':rec.delay_time,
                            'absent_check':rec.absent_check,
                            'absent_time':rec.absent_time,
                            'check_in':rec.check_in,
                            'attend_type':rec.attend_type,
                            }
                        rec.env['attendance.auto'].create(valus)

                        if rec.employee_id.attendance_approval == False:
                            email_template = rec.env.ref('attendance_automation.delay_employee_attendance')
                            if email_template:
                                if monthly_counter >= 2 :

                                    email_values = {
                                        'email_to': rec.employee_id.work_email,
                                        'email_from': rec.env.user.email,
                                    }
                                else:
                                    email_values = {
                                        'email_to': rec.employee_id.work_email,
                                        'email_from': rec.env.user.email,
                                        'email_cc' : rec.employee_id.parent_id.work_email,
                                    }
                                email_template.send_mail(rec.id, email_values=email_values)


                    elif rec.absent_check == True:
                        rec.attend_type = 'absent'
                        monthly_counter = monthly_counter + 1
                        month = date.today().strftime('%m')
                        check_in_month = rec.check_in.strftime('%m')
                        if month == check_in_month:
                            if all_attendace:
                                for line in all_attendace:
                                    if line:
                                        if line.check_in.strftime('%m') == month:
                                            if line.absent_check == True:
                                                monthly_counter = monthly_counter + 1
                        rec.employee_id.absent_monthly_counter = monthly_counter
                        
                        valus ={
                            'employee_id':rec.employee_id.id,
                            'department_id':rec.employee_id.department_id.id,
                            'delay_check':rec.delay_check,
                            'delay_time':rec.delay_time,
                            'absent_check':rec.absent_check,
                            'absent_time':rec.absent_time,
                            'check_in':rec.check_in,
                            'attend_type':rec.attend_type,
                            }
                        rec.env['attendance.auto'].create(valus)

                        if rec.employee_id.attendance_approval == False:
                            email_template = rec.env.ref('attendance_automation.absent_employee_attendance')
                            if email_template:
                                if monthly_counter >= 2 :

                                    email_values = {
                                        'email_to': rec.employee_id.work_email,
                                        'email_from': rec.env.user.email,
                                    }
                                else:
                                    email_values = {
                                        'email_to': rec.employee_id.work_email,
                                        'email_from': rec.env.user.email,
                                        'email_cc' : rec.employee_id.parent_id.work_email,
                                    }
                                email_template.send_mail(rec.id, email_values=email_values)


