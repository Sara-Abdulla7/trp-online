# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError,ValidationError
from datetime import date
from itertools import groupby

class ProjectKeffah(models.Model):
	_inherit = 'project.project'

	staff_ids = fields.One2many('project.staff', "project_id", "Staff")
	is_check = fields.Boolean(related="company_id.is_man_power", string='Is Check', readonly=True)
	project_income = fields.Float(string='Selling Price',readonly=True)
	sheet_ids = fields.One2many('time.sheet', "project_id", "TimeSheet")
	salary = fields.Float(string='Salary')
	order_ids = fields.One2many('order.line.keffah','project_order_id',string="Order Line")
	cost_count = fields.Integer(compute="compute_cost")

	instituionname= fields.Char(string="Instituion Name")
	email= fields.Char(string="Email")
	instituionnum= fields.Integer(string="Instituion Number")
	mobilenumber= fields.Integer(string="Mobile Number")
	contractnumber= fields.Integer(string="Contract Number")
	contractname= fields.Char(string="Contract Name")
	aboutthecontract= fields.Html(string="About The Contract")
	valueaadded= fields.Integer(string="Value Aadded")
	contractstart= fields.Date(string="Starting Date")
	contractend= fields.Date(string="End Date")
	multi_contract = fields.Many2many('ir.attachment','project_project_attachment_rel','project_id','attachment_id', string='Multi Contract Attachment',required=True)
	
	import_file = fields.Boolean(string="Import Employee")

	state = fields.Selection([
		('draft', 'Draft'),
		('confirm', 'Confirm'),
		('run', 'Running'),
		('close', 'Closed'),
		('cancel', 'Cancel'),
	], string='Status',
		track_visibility='onchange', help='Status of the Transport Operation', default='draft')
	sale_order_project_id = fields.Many2one('sale.order', string="Sale Order",readonly=True)
	timesheet_start_date = fields.Date(string="Timesheet date")
	timesheet_end_date = fields.Date()

	def action_confirm(self):
		for rec in self:
			if rec.is_check == True:
				rec.state = 'confirm'
				for line in rec.staff_ids:
					if line.laborer_status != "out of service" and line.laborer_status != "holiday" :
						line.laborer_status = "ready"
			else:
				return False
		self.hr_employee_state()
		self.import_file = False


	def test(self):
		action = self.env.ref('kefah_power.action_emp_import_wizard').read()[0]
		action.update({'views': [[False, 'form']]})
		return action


	@api.constrains('contractstart','contractend')
	def _check_date(self):
		for r in self:
			if r.contractstart > r.contractend:
				raise ValidationError("The Start Date Must be less than end date")

	def action_run(self):
		for rec in self:
			if rec.is_check == True:
				rec.state = 'run'
				self.transfer_staff_data()
			else:
				return False
		self.hr_employee_state()

	def action_close(self):
		for rec in self:
			if rec.is_check == True:
				rec.state = 'close'
				for line in rec.staff_ids:
					if line.laborer_status != "out of service" and line.laborer_status != "holiday" :
						line.laborer_status = "not_working"
			else:
				return False
		self.hr_employee_state()
		self.delete_transfer_staff_data()
		self.hr_employee_project_off()

	def action_cancel(self):
		for rec in self:
			if rec.is_check == True:
				rec.state = 'cancel'
				for line in rec.staff_ids:
					if line.laborer_status != "out of service" and line.laborer_status != "holiday" :
						line.laborer_status = "not_working"
			else:
				return False

		self.hr_employee_state()
		self.delete_transfer_staff_data()
		self.hr_employee_project_off()

	def action_reset_draft(self):
		for rec in self:
			if rec.is_check == True:
				rec.state = 'draft'
				for line in rec.staff_ids:
					if line.laborer_status != "out of service" and line.laborer_status != "holiday" :
						line.laborer_status = "ready"
			else:
				return False
		self.hr_employee_state()
		self.delete_transfer_staff_data()

	def delete_transfer_staff_data(self):
		project_detail_unlink = self.env['transfer.details'].search([('project_id','=',self.id)]).unlink()

	def transfer_staff_data(self):
		for rec in self:
			for line in rec.staff_ids:
				if line.laborer_status != "out of service":
					if line.laborer_status != "holiday":
						line.laborer_status = "working"
						valus ={
							'project_id':line.project_id.id,
							'employee_id':line.employee_id.id,
							'department_id':line.department_id.id,
							'job_id':line.all_keffah_line_ids.product_template_id.id,
							'hours_work':line.working_hours,
							'identification_no':line.identification_no,
							'state':line.laborer_status,
							}
						self.env['transfer.details'].create(valus)
					else:
						valus ={
							'project_id':line.project_id.id,
							'employee_id':line.employee_id.id,
							'department_id':line.department_id.id,
							'job_id':line.all_keffah_line_ids.product_template_id.id,
							'hours_work':line.working_hours,
							'identification_no':line.identification_no,
							'state':line.laborer_status,
							}
						self.env['transfer.details'].create(valus)						

	def hr_employee_state(self):
		for rec in self:
			for line in rec.staff_ids:
				hr_employee = self.env['hr.employee'].search([('id','=',line.employee_id.id)])
				for vals in hr_employee:
					vals.laborer_status = line.laborer_status
					if rec.state != 'close' or rec.state != 'cancel':
						vals.project_id = rec.id

	def hr_employee_project_off(self):
		for rec in self:
			emp = self.env['hr.employee'].search([('project_id','=',self._origin.id)])
			emp.project_id = False
			
	def get_analytic(self):
		self.ensure_one()
		return {
			'type': 'ir.actions.act_window',
			'name': "Analytic Account",
			'view_mode': 'tree',
			'res_model': "account.analytic.account",
			'domain': [('partner_id.id','=',self.partner_id.id),('company_id','=',self.company_id.id)],
			'context': {
			'create':False,
			'default_partner_id':self.partner_id.id,
			'default_company_id':self.company_id.id,
			}
		}

	def compute_cost(self):
		for record in self:
			record.cost_count = self.env['account.analytic.account'].search_count([('partner_id.id','=',self.partner_id.id),('company_id','=',self.company_id.id)])


class ProjectStaffKeffah(models.Model):
	_name = 'project.staff'

	project_id = fields.Many2one('project.project',string='Project')
	employee_id = fields.Many2one('hr.employee',string='Laborers' ,domain=[('laborer', '=', 'True'),('in_project', '!=', 'True')])
	identification_no = fields.Char(string='Identification No')
	department_id = fields.Many2one('department.line.keffah',string='Department')
	job_position_id = fields.Many2one('product.product',string='Job Position')
	all_keffah_line_ids = fields.Many2one('order.line.keffah',string="Job Position")
	working_hours = fields.Float(string="Working Hours")
	laborer_status = fields.Selection([('working', 'Working'),('not_working','Not Working'),('ready', 'Ready'),('transferred', 'The Employee Has Been Transferred'),('out of service', 'Out Of Service'),('holiday','Holiday'),],default='ready' ,string="Laborer Status")
	all_orders_ids = fields.One2many('order.line.keffah','working_days','working_hours')
	test_ids=fields.Many2many('department.line.keffah',compute='department_domain')

	@api.onchange('department_id')
	@api.depends('department_id')
	def department_domain(self):
		department_obj = self.env['department.department.keffah'].search([('company_name_id.id','=',self.project_id._origin.id)]).mapped('department_ids')
		for rec in self:
			rec.test_ids=[(6,0,department_obj.ids)]

	def get_employee(self):
		if self.employee_id: 
			self.identification_no = self.employee_id.identification_id

	@api.onchange('employee_id')
	def get_employees(self):
		if self.employee_id: 
			self.identification_no = self.employee_id.identification_id

	@api.onchange('employee_id')
	def let_employee_check_true(self):
		if self.employee_id:
			self.employee_id.is_check = True

	@api.onchange('employee_id')
	def change_job_domain(self):
		order_line_kefah= self.env['order.line.keffah'].search([('project_order_id','=',self.project_id._origin.id)]).mapped('product_template_id.id')

		return {'domain': {'job_position_id':[('id','in',order_line_kefah)]}}


	@api.onchange('employee_id')
	def change_job_domain(self):	
		all_keffah_line_ids= self.env['order.line.keffah'].search([('project_order_id','=',self.project_id._origin.id)])
		return {'domain': {'all_keffah_line_ids':[('id','in',all_keffah_line_ids.ids)]}}

	@api.onchange('employee_id')
	def get_employee_recoreds(self):
			emp = self.env['hr.employee'].search([('laborer','=','True'),('id','=',self.employee_id.id)])
			emp.update({
				'in_project':True
				})

	def create(self,vals):
		res = super(ProjectStaffKeffah, self).create(vals)
		res.employee_id.update({
				'in_project':False
				})
		return res

	@api.onchange('employee_id')
	def get_employee_recored(self):
		emp_in_project = self.env['project.project'].search([('state','=',['draft','run'])]).mapped('staff_ids.employee_id.id')
		hr_repo = self.env['hr.employee'].search([('laborer','=','True'),('id','=',emp_in_project)])
		return{'domain': {'employee_id':[('id','not in',hr_repo.ids),('laborer_status','!=','out of service'),('laborer','=','True'),('in_project','!=','True')]}}


class TimeSheetKeffah(models.Model):
	_name = 'time.sheet'

	project_id = fields.Many2one('project.project',string='Project')
	
	data_request = fields.Date(string="Request Date",readonly=True)
	split = fields.Selection([('consolidated', 'Consolidated Invoice'),('separate', 'Separate Invoice'),],string="Invoice type",default='consolidated',readonly=True)
	ot_line_subtotal = fields.Float(string="OT Subtotal",readonly='True')
	salary_line_subtotal = fields.Float(string="Salary Subtotal",readonly='True')
	ot_salary_subtotal = fields.Float(string="Subtotal Payment",readonly='True')

class OrderLineKeffah(models.Model):
	_name = 'order.line.keffah'

	project_order_id = fields.Many2one('project.project',string='Project')
	product_template_id = fields.Many2one('product.product',string='Product')
	working_days = fields.Many2one('work.day',string="Working Days")
	working_hours = fields.Many2one('work.hours',string="Working Hours")
	quantity = fields.Float(string="Quantity")
	price_unit = fields.Float(string="Unit Price")

	total_monthly = fields.Float(string="Total Monthly")
	working_month = fields.Many2one('work.monthly',string="Monthly Working Period")
	price_subtotal = fields.Float(string="Subtotal")

	ot_percent = fields.Float(string="OT Percent")
	all_orders_ids = fields.Many2one('project.staff')

	resale = fields.Char(string="Resale")

	all_keffah_line_ids = fields.One2many('project.staff','project_id',string="Job Position")


	def name_get(self):
		res=[]
		for rec in self:
			if rec.resale == False:
				name=    f"{rec.product_template_id.name}"
			else:
				name=  f"{rec.resale} - {rec.product_template_id.name} "

			res.append((rec.id,name))
		return res

class ReorderLineKeffah(models.Model):
	_name = 'reorder.line.keffah'
	_rec_name = "product_template_id"

	project_reorder_id = fields.Many2one('project.project',string='Project')
	product_template_id = fields.Many2one('product.product',string='Product')
	working_days = fields.Many2one('work.day',string="Working Days")
	working_hours = fields.Many2one('work.hours',string="Working Hours")
	quantity = fields.Float(string="Quantity")
	price_unit = fields.Float(string="Unit Price")

	total_monthly = fields.Float(string="Total Monthly")
	working_month = fields.Many2one('work.monthly',string="Monthly Working Period")
	price_subtotal = fields.Float(string="Subtotal")

	ot_percent = fields.Float(string="OT Percent")
	all_orders_ids = fields.Many2one('project.staff')


class DepartmentKeffah(models.Model):
	_name = 'department.department.keffah'
	_inherit = ['mail.thread','mail.activity.mixin']
	_rec_name = 'company_name_id'

	company_name_id = fields.Many2one('project.project',string='Project Name')
	department_ids = fields.One2many('department.line.keffah','department_id',string="Order Line")
	data_request = fields.Date(string="Request Date", default=fields.Datetime.now)

class DepartmentLineKeffah(models.Model):
	_name = 'department.line.keffah'
	_rec_name = 'name_english'

	department_id = fields.Many2one('department.department.keffah',string='Project')
	name_english  = fields.Char(string='English Department Name')
	name_arabic  = fields.Char(string='Arabic Department Name')


