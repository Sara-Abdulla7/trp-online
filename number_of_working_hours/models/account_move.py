from odoo import models, fields, api


class Account_move(models.Model):
	_inherit='account.move'

	total_hours = fields.Integer(readonly="True")
	hours = fields.Integer(compute='hour_compute',readonly=True ,string='Total Hours')

	total_employees = fields.Integer(readonly="True")
	compute_employees = fields.Integer(compute='employee_compute',readonly=True ,string='Total Employees')
	company_boolean= fields.Boolean(related='company_id.is_man_power')

	def hour_compute(self):
		for rec in self.invoice_line_ids:
			self.hours += rec.quantity
		self.total_hours = self.hours

	def employee_compute(self):
		for rec in self.invoice_line_ids:
			self.compute_employees += rec.number_employees
		self.total_employees = self.compute_employees



class Account_move_line(models.Model):
	_inherit='account.move.line'

	number_employees = fields.Integer(String="No employees")
	test_check=fields.Boolean()
	company_boolean= fields.Boolean(related='company_id.is_man_power')