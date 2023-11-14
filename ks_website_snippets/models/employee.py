from datetime import date, datetime, timedelta
from odoo import models
import base64


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def automated_scheduler_send_individual_report(self):
        employees = self.env['hr.employee'].search([])
        for emp_obj in employees:
            vals = self.get_individual_performance(emp_obj.id)
            data = {
                'vals': [vals]
            }
            report = self.env['ir.actions.report']._render_qweb_pdf(
                'ks_website_snippets.action_employees_performance_individual_report_pdf',
                self, data=data)
            data_record = base64.b64encode(report[0])
            ir_values = {
                'name': "Employees Performance Report",
                'type': 'binary',
                'datas': data_record,
                'store_fname': data_record,
                'mimetype': 'application/pdf',
            }
            attachment1 = self.env['ir.attachment'].create(ir_values)
            mail_values = {
                'email_to': emp_obj.work_email,
                'subject': 'Performance Report',
                "attachment_ids": [attachment1.id]
            }
            mail = self.env["mail.mail"].sudo().create(mail_values)
            mail.send()

    def get_all_performance(self):
        result = self.get_all_performance_data()
        return result

    def get_all_performance_data(self):
        current_date = date.today()
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        end_date = current_date.strftime('%Y-%m-%d')
        num_working_days = 0
        end = datetime.now()
        start = datetime.now() - timedelta(days=30)
        while start <= end:
            if start.weekday() < 5:
                num_working_days += 1
            start += timedelta(days=1)
        attendance = self.env['hr.attendance'].search([
            ('check_in', '>=', start_date), ('check_in', '<=', end_date)])
        worked_hours_per_employee = {}
        for rec in attendance:
            employee_id = rec.employee_id
            worked_hours = rec.worked_hours
            if employee_id in worked_hours_per_employee:
                worked_hours_per_employee[employee_id] += worked_hours
            else:
                worked_hours_per_employee[employee_id] = worked_hours
        performance_attendance = {}
        for employee_id, total_worked_hours in worked_hours_per_employee.items():
            hours_total = employee_id.resource_calendar_id.hours_per_day * num_working_days
            worked_hours_total = total_worked_hours
            average = (worked_hours_total/hours_total)*100 if\
                (worked_hours_total/hours_total)*100 < 101 else 100
            employee_id = employee_id
            if employee_id in performance_attendance:
                performance_attendance[employee_id] += average
            else:
                performance_attendance[employee_id] = average
        tasks = self.env['project.task'].sudo().search([
            ('date_deadline', '>=', start_date),
            ('date_deadline', '<=', end_date),
            ('is_closed', '=', True)])
        task_details = {}
        for rec in tasks:
            for user in rec.user_ids:
                employee_id = self.env['hr.employee'].sudo().search([('user_id', '=', user.id)])
                if employee_id in task_details:
                    task_details[employee_id] += 1
                else:
                    task_details[employee_id] = 1
        sorted_attendance = {k: v for k, v in
                             sorted(performance_attendance.items(),
                                    key=lambda item: item[1], reverse=True)}
        combined_performance = {}
        for employee_id, attendance_percentage in sorted_attendance.items():
            task_count = task_details.get(employee_id, 0)
            attendance_scaled = attendance_percentage
            performance = (attendance_scaled + (task_count * 20)) / 2
            combined_performance[employee_id] = {
                'Attendance': attendance_percentage,
                'Task Count': task_count,
                'Performance': performance,
                'attendance': attendance_scaled,
                'task': task_count*10
            }
        sorted_performance = {k: v for k, v in
                              sorted(combined_performance.items(),
                                     key=lambda item: item[1]['Performance'],
                                     reverse=True)}
        vals = []
        for employee_id, performance in sorted_performance.items():
            vals.append({
                'id': employee_id.id,
                'name': employee_id.name,
                'Performance': performance['Performance'],
                'attendance': performance['attendance'],
                'task': performance['task'],
                'rounded': round(performance['Performance'], 1) if
                performance['Performance'] < 101 else 100,
                'rounded_t': round(performance['task'], 1) if
                performance['task'] < 101 else 100,
                'rounded_a': round(performance['attendance'], 1) if
                performance['attendance'] < 101 else 100
            })
        return vals

    def get_performance(self):
        result = self.get_individual_performance(self.id)
        return [result]

    def get_individual_performance(self, id):
        current_date = date.today()
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        end_date = current_date.strftime('%Y-%m-%d')
        num_working_days = 0
        end = datetime.now()
        start = datetime.now() - timedelta(days=30)
        while start <= end:
            if start.weekday() < 5:
                num_working_days += 1
            start += timedelta(days=1)
        attendance = self.env['hr.attendance'].search([
            ('employee_id', '=', id),
            ('check_in', '>=', start_date),
            ('check_in', '<=', end_date)
        ])
        worked_hours_total = sum(attendance.mapped('worked_hours'))
        employee_id = self.env['hr.employee'].sudo().browse(id)
        hours_total = \
            employee_id.resource_calendar_id.hours_per_day * num_working_days
        average = (worked_hours_total / hours_total) * 100 if \
            (worked_hours_total / hours_total) * 100 < 101 else 100
        tasks = self.env['project.task'].sudo().search([
            ('user_ids', 'in', employee_id.user_id.id),
            ('date_deadline', '>=', start_date),
            ('date_deadline', '<=', end_date),
            ('is_closed', '=', True)
        ])
        task_count = len(tasks)
        attendance_scaled = average
        performance = (attendance_scaled + (task_count * 20)) / 2
        data = {
            'id': employee_id.id,
            'name': employee_id.name,
            'Performance': performance,
            'attendance': attendance_scaled,
            'task': task_count * 10,
            'rounded': round(performance, 1) if performance < 101 else 100,
            'rounded_t': round(task_count * 10,
                               1) if (task_count * 10) < 101 else 100,
            'rounded_a': round(attendance_scaled,
                               1) if attendance_scaled < 101 else 100
        }
        return data

    def automated_scheduler_send_report(self):
        current_date = date.today()
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        end_date = current_date.strftime('%Y-%m-%d')
        num_working_days = 0
        end = datetime.now()
        start = datetime.now() - timedelta(days=30)
        while start <= end:
            if start.weekday() < 5:
                num_working_days += 1
            start += timedelta(days=1)
        attendance = self.env['hr.attendance'].search([
            ('check_in', '>=', start_date), ('check_in', '<=', end_date)])
        worked_hours_per_employee = {}
        for rec in attendance:
            employee_id = rec.employee_id
            worked_hours = rec.worked_hours
            if employee_id in worked_hours_per_employee:
                worked_hours_per_employee[employee_id] += worked_hours
            else:
                worked_hours_per_employee[employee_id] = worked_hours
        performance_attendance = {}
        for employee_id, total_worked_hours in worked_hours_per_employee.items():
            hours_total = employee_id.resource_calendar_id.hours_per_day * num_working_days
            worked_hours_total = total_worked_hours
            average = (worked_hours_total/hours_total)*100 if\
                (worked_hours_total/hours_total)*100 < 101 else 100
            employee_id = employee_id
            if employee_id in performance_attendance:
                performance_attendance[employee_id] += average
            else:
                performance_attendance[employee_id] = average
        tasks = self.env['project.task'].sudo().search([
            ('date_deadline', '>=', start_date),
            ('date_deadline', '<=', end_date),
            ('is_closed', '=', True)])
        task_details = {}
        for rec in tasks:
            for user in rec.user_ids:
                employee_id = self.env['hr.employee'].sudo().search([('user_id', '=', user.id)])
                if employee_id in task_details:
                    task_details[employee_id] += 1
                else:
                    task_details[employee_id] = 1
        sorted_attendance = {k: v for k, v in
                             sorted(performance_attendance.items(),
                                    key=lambda item: item[1], reverse=True)}
        combined_performance = {}
        for employee_id, attendance_percentage in sorted_attendance.items():
            task_count = task_details.get(employee_id, 0)
            attendance_scaled = attendance_percentage
            performance = (attendance_scaled + (task_count * 20)) / 2
            combined_performance[employee_id] = {
                'Attendance': attendance_percentage,
                'Task Count': task_count,
                'Performance': performance,
                'attendance': attendance_scaled,
                'task': task_count*10
            }
        sorted_performance = {k: v for k, v in
                              sorted(combined_performance.items(),
                                     key=lambda item: item[1]['Performance'],
                                     reverse=True)}
        vals = []
        for employee_id, performance in sorted_performance.items():
            vals.append({
                'id': employee_id.id,
                'name': employee_id.name,
                'Performance': performance['Performance'],
                'attendance': performance['attendance'],
                'task': performance['task'],
                'rounded': round(performance['Performance'], 1) if
                performance['Performance'] < 101 else 100,
                'rounded_t': round(performance['task'], 1) if
                performance['task'] < 101 else 100,
                'rounded_a': round(performance['attendance'], 1) if
                performance['attendance'] < 101 else 100
            })
        data = {
            'vals': vals
        }
        report = self.env['ir.actions.report']._render_qweb_pdf(
            'ks_website_snippets.action_employees_performance_report_pdf',
            self, data=data)
        data_record = base64.b64encode(report[0])
        ir_values = {
            'name': "Employees Performance Report",
            'type': 'binary',
            'datas': data_record,
            'store_fname': data_record,
            'mimetype': 'application/pdf',
        }
        attachment1 = self.env['ir.attachment'].create(ir_values)
        mail_values = {
            'email_to': self.env.company.email,
            'subject': 'Employees Performance Report',
            "attachment_ids": [attachment1.id]
        }
        mail = self.env["mail.mail"].sudo().create(mail_values)
        mail.send()

    def get_top_10_employees_by_attendance(self):
        current_date = date.today()
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        end_date = current_date.strftime('%Y-%m-%d')
        num_working_days = 0
        end = datetime.now()
        start = datetime.now() - timedelta(days=30)
        while start <= end:
            if start.weekday() < 5:
                num_working_days += 1
            start += timedelta(days=1)
        attendance = self.env['hr.attendance'].search([
            ('check_in', '>=', start_date), ('check_in', '<=', end_date)])
        worked_hours_per_employee = {}
        for rec in attendance:
            employee_id = rec.employee_id
            worked_hours = rec.worked_hours
            if employee_id in worked_hours_per_employee:
                worked_hours_per_employee[employee_id] += worked_hours
            else:
                worked_hours_per_employee[employee_id] = worked_hours
        performance_attendance = {}
        for employee_id, total_worked_hours in worked_hours_per_employee.items():
            hours_total = employee_id.resource_calendar_id.hours_per_day * num_working_days
            worked_hours_total = total_worked_hours
            average = (worked_hours_total / hours_total) * 100
            employee_id = employee_id
            if employee_id in performance_attendance:
                performance_attendance[employee_id.id] += average
            else:
                performance_attendance[employee_id.id] = average
        sorted_attendance = sorted(performance_attendance.items(),
                                   key=lambda x: x[1], reverse=True)
        top_10_employees = self.browse([int(r[0]) for r in
                                        sorted_attendance[:10]])
        return top_10_employees

    def get_top_10_employees_by_project_tasks(self):
        current_date = date.today()
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        end_date = current_date.strftime('%Y-%m-%d')
        num_working_days = 0
        end = datetime.now()
        start = datetime.now() - timedelta(days=30)
        while start <= end:
            if start.weekday() < 5:
                num_working_days += 1
            start += timedelta(days=1)
        tasks = self.env['project.task'].sudo().search([
            ('date_deadline', '>=', start_date),
            ('date_deadline', '<=', end_date),
            ('is_closed', '=', True)])
        task_details = {}
        for rec in tasks:
            for user in rec.user_ids:
                employee_id = self.env['hr.employee'].sudo().search(
                    [('user_id', '=', user.id)])
                if employee_id in task_details:
                    task_details[employee_id] += 1
                else:
                    task_details[employee_id] = 1
        tasks_data = sorted(task_details.items(),
                                   key=lambda x: x[1], reverse=True)
        top_10_employees = self.browse([int(r[0]) for r in tasks_data])
        return top_10_employees

    def get_top_10_employees_combined(self):
        current_date = date.today()
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        end_date = current_date.strftime('%Y-%m-%d')
        num_working_days = 0
        end = datetime.now()
        start = datetime.now() - timedelta(days=30)
        while start <= end:
            if start.weekday() < 5:
                num_working_days += 1
            start += timedelta(days=1)
        attendance = self.env['hr.attendance'].search([
            ('check_in', '>=', start_date), ('check_in', '<=', end_date)])
        worked_hours_per_employee = {}
        for rec in attendance:
            employee_id = rec.employee_id
            worked_hours = rec.worked_hours
            if employee_id in worked_hours_per_employee:
                worked_hours_per_employee[employee_id] += worked_hours
            else:
                worked_hours_per_employee[employee_id] = worked_hours
        performance_attendance = {}
        for employee_id, total_worked_hours in worked_hours_per_employee.items():
            hours_total = employee_id.resource_calendar_id.hours_per_day * num_working_days
            worked_hours_total = total_worked_hours
            average = (worked_hours_total / hours_total) * 100
            employee_id = employee_id
            if employee_id in performance_attendance:
                performance_attendance[employee_id] += average
            else:
                performance_attendance[employee_id] = average
        tasks = self.env['project.task'].sudo().search([
            ('date_deadline', '>=', start_date),
            ('date_deadline', '<=', end_date),
            ('is_closed', '=', True)])
        task_details = {}
        for rec in tasks:
            for user in rec.user_ids:
                employee_id = self.env['hr.employee'].sudo().search(
                    [('user_id', '=', user.id)])
                if employee_id in task_details:
                    task_details[employee_id] += 1
                else:
                    task_details[employee_id] = 1
        sorted_attendance = {k: v for k, v in
                             sorted(performance_attendance.items(),
                                    key=lambda item: item[1], reverse=True)}
        combined_performance = {}
        for employee_id, attendance_percentage in sorted_attendance.items():
            task_count = task_details.get(employee_id, 0)
            attendance_scaled = attendance_percentage
            performance = (attendance_scaled + (task_count * 10)) / 2
            combined_performance[employee_id] = {
                'Attendance': attendance_percentage,
                'Task Count': task_count,
                'Performance': performance
            }
        sorted_performance = sorted(combined_performance.items(),
                                    key=lambda item: item[1]['Performance'],
                                    reverse=True)
        top_10_employees = self.browse(
            [int(r[0]) for r in sorted_performance[:10]])
        return top_10_employees
