from odoo import models, fields, api, _
from datetime import date



class Old_salary(models.Model):
	_name="old.salary"

	employee_id = fields.Many2one('hr.employee',string='Employee',readonly=True)

	project_id = fields.Many2one('project.project',string='Project',readonly=True)
	project_id_to = fields.Many2one('project.project',string='To Project',readonly=True)

	transfer_date = fields.Date(string="Transfer Date",default=fields.Datetime.now,readonly=True)

	old_department_id = fields.Many2one('department.line.keffah',string='Old Department',readonly=True)

	old_working_hours = fields.Float(string="Old Working Hours ",readonly=True)
	salary = fields.Float(string="Salary",readonly=True)

	active = fields.Boolean(string="Active",readonly=True)


	def name_get(self):
		res=[]
		for rec in self:
			name=  f" {rec.employee_id.name}"
			res.append((rec.id,name))
		return res


