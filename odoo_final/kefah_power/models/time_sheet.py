# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError,ValidationError
import calendar 
from calendar import monthrange
from itertools import groupby
import base64
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import pandas as pd
from dateutil.rrule import *

class TimeSheetDetailsKeffah(models.Model):
	_name = 'time.sheet.details'
	_inherit = ['mail.thread','mail.activity.mixin']
	_rec_name = 'project_id'
	_order = 'id desc'

	project_id = fields.Many2one('project.project',string='Project',domain=[('state', '=', 'run')])
	data_request = fields.Date(string="Request Date", default=fields.Datetime.now)
	split = fields.Selection([
		('consolidated', 'Consolidated Invoice'),
		('separate', 'Separate Invoice'),
	],string="Invoice type",default="consolidated")

	time_sheet_type = fields.Selection([('each_departments','For All Departments'),('department','For One Department')],string="TimeSheet Type")
	department_id = fields.Many2one('department.line.keffah',string="Department")
	department_name_arabic = fields.Many2one('department.line.keffah',string="Arabic Department")
	name_arabic = fields.Char(string="Arabic Department")


	type_month = fields.Selection([
		('this', 'This Month'),
		('last', 'Last Month'),
	],string="Month Type")
	month = fields.Integer(string="Working Days",readonly='True')

	holiday_total = fields.Integer(string="OF Day")

	holiday_ids = fields.Many2many('holiday.time.sheet',string="Holiday TimeSheet" )
	is_holiday = fields.Selection(  
		[
		('zero', '0'),
		('one', '1'),
		
		],
		string="Is Holiday",default='zero')

	timesheet_start_date = fields.Date(string="Timesheet date")
	timesheet_end_date = fields.Date()

	user_id = fields.Many2one('res.users',string="Project Manager")
	date_timesheet = fields.Date(string='TimeSheet Date')

	timesheet_order_ids = fields.One2many('time.sheet.line','timesheet_id',string='TimeSheet')
	timesheet_order_ot_ids = fields.One2many('time.sheet.line','timesheet_ot_id',string='TimeSheet OT')
	state = fields.Selection([
		('draft', 'Draft'),
		('confirm', 'Confirm'),
		('done', 'Done'),
		('cancel', 'Cancel'),
	], string='Status',
		track_visibility='onchange', help='Status of the Transport Operation', tracking=True ,default='draft')

	timesheet_start_date = fields.Date(string="Timesheet date")
	timesheet_end_date = fields.Date()

	sale_order_project_id = fields.Many2one('sale.order', string="Sale Order",readonly=True)

	standard = fields.Selection([('208', '208'),('260', '260'),('372', '372'),], string='Standard',
		track_visibility='onchange', help='Employee Operating Standard')

	number_employees = fields.Integer(string="No Employee")


	ot_line_subtotal = fields.Float(string="OT Subtotal",readonly='True',store=True, compute='compute_ot')
	salary_line_subtotal = fields.Float(string="Salary Subtotal",readonly='True',store=True, compute='amount_salary_sheet')
	ot_salary_subtotal = fields.Float(string="Subtotal Payment",readonly='True',store=True, compute='amount_salary_ot_sheet')
	attachment_ids = fields.Many2many(
        comodel_name='ir.attachment',
        string="Attachments",
    )

	@api.onchange('time_sheet_type')
	def change_time_sheet_type(self):
		if self.time_sheet_type == 'department':
			department = self.env['department.department.keffah'].search([('company_name_id','=',self.project_id.id)]).mapped('department_ids')
			print('sssssssssssssssssss',department)
			return {'domain': {'department_id':[('id','in',department.ids)]}}


	@api.onchange('project_id')
	def get_sale_order_down_paymenr(self):
		if self.project_id:
			self.sale_order_project_id = self.project_id.sale_order_project_id.id


	@api.onchange('timesheet_start_date','timesheet_end_date','holiday_total')
	def _git_month(self):
		if self.timesheet_start_date and self.timesheet_start_date:
			for rec in self:
				with_out_fridays = []
				start_date = datetime.strptime(str(self.timesheet_start_date),'%Y-%m-%d').date()
				start_end = datetime.strptime(str(self.timesheet_end_date),'%Y-%m-%d').date()			
				a = pd.date_range(start_date,start_end)
				for i in a:
					with_out_fridays.append(i.date())
					langth = len(with_out_fridays)
				self.month = int(float(langth) - self.holiday_total)


	@api.onchange('timesheet_end_date')
	def git_timesheet_values(self):
		if self.timesheet_end_date:
			self.is_holiday = 'one'
		else:
			self.is_holiday = 'zero'

	@api.onchange('holiday_ids')
	def git_data_holiday_ids(self):
		if not self.holiday_ids:
			self.holiday_total = 0.0

	# @api.depends('holiday_ids')
	# def git_holiday_ids(self):
	# 	if self.holiday_ids:
	# 		for rec in self:
	# 			holiday = rec.mapped('holiday_ids')
	# 			ranges = len(holiday)
	# 			if ranges == 2:
	# 				fridays = []
	# 				day = []
	# 				new_set = set()
	# 				with_out_fridays = []

	# 				saturday = []
	# 				day_2 = []
	# 				new_set_2 = set()
	# 				with_out_fridays_2 = []
	# 				start_date = datetime.strptime(str(self.timesheet_start_date),'%Y-%m-%d').date()
	# 				start_end = datetime.strptime(str(self.timesheet_end_date),'%Y-%m-%d').date()
	# 				a = pd.date_range(start_date,start_end)
	# 				for i in a:
	# 					with_out_fridays_2.append(i.date())
	# 					with_out_fridays.append(i.date())

	# 				for i in a:
	# 					fridays.append(i.date() - (relativedelta(weekday=FR(-1))))
	# 					saturday.append(i.date() - (relativedelta(weekday=SA(1))))

	# 					for records in fridays:
	# 						day.append(records.day)
	# 					for recordion in saturday:
	# 						day_2.append(recordion.day)
	# 				for data in day:
	# 					new_set.add(data)

	# 				for data in day_2:
	# 					new_set_2.add(data)

	# 				set_len = len(new_set)
	# 				set_len_2 = len(new_set_2)
	# 				days =  (set_len - 1) + set_len_2 -1
	# 				self.holiday_total = int(days)
	# 			else:
	# 				if 1 == holiday.holiday_id:
	# 					fridays = []
	# 					day = []
	# 					new_set = set()
	# 					with_out_fridays = []
	# 					start_date = datetime.strptime(str(self.timesheet_start_date),'%Y-%m-%d').date()
	# 					start_end = datetime.strptime(str(self.timesheet_end_date),'%Y-%m-%d').date()			
	# 					a = pd.date_range(start_date,start_end)
	# 					for i in a:
	# 						with_out_fridays.append(i.date())
	# 					for i in a:
	# 						fridays.append(i.date() - (relativedelta(weekday=FR(-1))))
	# 						for records in fridays:
	# 							day.append(records.day)
	# 					for data in day:
	# 						new_set.add(data)
	# 					set_len = len(new_set)
	# 					self.holiday_total = int(set_len - 1)

	# 				else:
	# 					saturday = []
	# 					day_2 = []
	# 					new_set_2 = set()
	# 					with_out_fridays_2 = []
	# 					start_date = datetime.strptime(str(self.timesheet_start_date),'%Y-%m-%d').date()
	# 					start_end = datetime.strptime(str(self.timesheet_end_date),'%Y-%m-%d').date()			
	# 					a = pd.date_range(start_date,start_end)

	# 					for i in a:
	# 						with_out_fridays_2.append(i.date())

	# 					for i in a:
	# 						saturday.append(i.date() - (relativedelta(weekday=SA(1))))
	# 						for records in saturday:
	# 							day_2.append(records.day)

	# 					for data in day_2:
	# 						new_set_2.add(data)
	# 					set_len = len(new_set_2)
	# 					self.holiday_total =  int(set_len - 1)

				
	@api.onchange('department_id')
	def check_time_sheet_monthly(self):
		month = date.today().strftime('%m')
		is_check = False
		search_same_project = self.env['time.sheet.details'].search([('project_id','=',self.project_id.id)])
		for rec in search_same_project:
			rec_month = rec.data_request.strftime('%m')
			if rec_month == month and rec.department_id.id == self.department_id.id:
				is_check = True
				break
		if is_check == True:
			raise UserError(('You Already did This Timesheet For This Department In This Month!'))


	@api.depends('timesheet_order_ot_ids.ot_total')
	def compute_ot(self):
		for rec in self:
			rec.ot_line_subtotal = sum(line.ot_total for line in rec.timesheet_order_ot_ids)


	@api.depends('timesheet_order_ids.salary')
	def amount_salary_sheet(self):
		for rec in self:
			rec.salary_line_subtotal = sum(line.total for line in rec.timesheet_order_ids)

	@api.depends('ot_line_subtotal','salary_line_subtotal')
	def amount_salary_ot_sheet(self):
		for rec in self:
			rec.ot_salary_subtotal = rec.ot_line_subtotal + rec.salary_line_subtotal

	def submit_confirm(self):
		for rec in self:
			rec.state = 'confirm'
			rec.is_holiday = 'zero'


	def reset_to_draft(self):
		for rec in self:
			rec.state = 'draft'
			rec.is_holiday = 'one'

	def submit_done(self):
		for rec in self:
			rec.state = 'done'
			rec.is_holiday = 'zero'
			if rec.split == 'consolidated':
				product = []
				records = []
				ot_line = []
				
				order_id = self.env['sale.order'].search([('id','=',rec.sale_order_project_id.id)])
				for line in rec.timesheet_order_ids:
					product.append(line.all_keffah_line_ids.product_template_id.id)  
				print(product)  
				salla = set(product)
				for data in salla:
					itmes = self.env['time.sheet.line'].search([('timesheet_id','=',self.timesheet_order_ids.timesheet_id.id),('all_keffah_line_ids.product_template_id','=',data)])
					working_hours = sum(itmes.mapped('working_hours'))
					salary = itmes.mapped('unit_price')[0]
					records.append((data,working_hours,salary))

				if order_id:
					valus = {
					'advance_payment_method':'fixed',
					'fixed_amount':rec.ot_salary_subtotal
					}
					down_payment_register_obj = self.env['sale.advance.payment.inv'].with_context({'active_model':'sale.order','active_ids':order_id.ids}).create(valus)
					down_payment_register_obj.create_invoices()

					invoice = self.env['account.move'].search([('state','=','draft'),('move_type','=','out_invoice'),('sale_orders_id','=',rec.sale_order_project_id.id)],limit=1)
					for inv in invoice:
						for line in inv:
							line.invoice_line_ids = [(5, 0, 0)]
							line.update({
								'department_sheet':self.department_id.id,
								'start_date':self.timesheet_start_date,
								'end_date':self.timesheet_end_date,
								'number_employees':self.number_employees,
								'The_number_of_working_days':self.month,
								'department_arabic':self.name_arabic
								})
							line.write({
								'department_arabic':self.name_arabic
								})

							line.update({'invoice_line_ids':[(0, 0,
							 {'move_id':invoice.id,
							  'product_id':itmes[0],
							  'quantity':itmes[1],
							  'price_unit':itmes[2],
							  })for itmes in records]})

							line.update({'invoice_line_ids':[(0, 0,
							 {'move_id':invoice.id,
							  'product_id':line.job_position_id.id,
							  'quantity':line.ot,
							  'price_unit':line.ot_price,
							  })for line in rec.timesheet_order_ot_ids]})

							self.get_attachment(invoice.id)
							self.push_time_sheet_info()
						return {
						'effect': {
				        'fadeout': 'slow',
				        'message': 'تم اجراء النقلية بنجاح ',
				        'type': 'rainbow_man'}
				        }

			else:
				product = []
				records = []
				ot_line = []

				order_id = self.env['sale.order'].search([('id','=',rec.sale_order_project_id.id)])
				for line in rec.timesheet_order_ids:
					product.append(line.all_keffah_line_ids.product_template_id.id)


				salla = set(product)
				for data in salla:
					itmes = self.env['time.sheet.line'].search([('timesheet_id','=',self.timesheet_order_ids.timesheet_id.id),('all_keffah_line_ids.product_template_id','=',data)])
					working_hours = sum(itmes.mapped('working_hours'))
					salary = sum(itmes.mapped('salary')) / working_hours
					records.append((data,working_hours,salary))


				if order_id:
					valus = {
					'advance_payment_method':'fixed',
					'fixed_amount':rec.salary_line_subtotal
					}
					down_payment_register_obj = self.env['sale.advance.payment.inv'].with_context({'active_model':'sale.order','active_ids':order_id.ids}).create(valus)
					down_payment_register_obj.create_invoices()

					invoice = self.env['account.move'].sudo().search([('state','=','draft'),('move_type','=','out_invoice'),('sale_orders_id','=',rec.sale_order_project_id.id)],limit=1)
					
					for inv in invoice:
						for line in inv:
							line.invoice_line_ids = [(5, 0, 0)]
							line.update({
								'department_sheet':self.department_id.id,
								'start_date':self.timesheet_start_date,
								'end_date':self.timesheet_end_date,
								'number_employees':self.number_employees,
								'The_number_of_working_days':self.month,
								'department_arabic':self.name_arabic
								})
							line.write({
								'department_arabic':self.name_arabic
								})
							line.update({'invoice_line_ids':[(0, 0,
							 {'move_id':invoice.id,
							  'product_id':itmes[0],
							  'quantity':itmes[1],
							  'price_unit':itmes[2],
							  })for itmes in records]})

							self.get_attachment(invoice.id)
							self.push_time_sheet_info()

				if order_id:
					valus = {
					'advance_payment_method':'fixed',
					'fixed_amount':rec.ot_line_subtotal
					}
					down_payment_register_obj = self.env['sale.advance.payment.inv'].with_context({'active_model':'sale.order','active_ids':order_id.ids}).create(valus)
					down_payment_register_obj.create_invoices()


					invoice_2 = self.env['account.move'].search([('state','=','draft'),('move_type','=','out_invoice'),('sale_orders_id','=',rec.sale_order_project_id.id)],limit=1)

					for inv2 in invoice_2:
						for line in inv2:
							line.invoice_line_ids = [(5, 0, 0)]
							line.update({'invoice_line_ids':[(0, 0,
							 {'move_id':invoice_2.id,
							  'product_id':line.job_position_id.id,
							  'quantity':line.ot,
							  'price_unit':line.ot_price,
							  })for line in rec.timesheet_order_ot_ids.filtered(lambda r: r.ot > 0)]})
				return {
				'effect': {
		        'fadeout': 'slow',
		        'message': 'تم اجراء النقلية بنجاح ',
		        'type': 'rainbow_man'}
		        }

	def submit_cancel(self):
		for rec in self:
			rec.state = 'cancel'
			rec.is_holiday = 'zero'


	def get_attachment(self,valus):
		attachment = []
		for rec in self:
			for line in rec.attachment_ids:
				attachment.append((line.name,line.type,line.datas,line.store_fname,line.mimetype))
		if attachment:
			for att in attachment:
				valus_ir = {
					'name': att[0],
					'type': att[1],
					'datas': base64.b64encode(att[2]),
					'store_fname': att[3],
					'res_model':'account.move',
					'res_id': valus,
					'mimetype':att[4]
					}
			self.env['ir.attachment'].sudo().write(valus_ir)
			ir = self.env['ir.attachment'].search([('res_id','=',rec.id)])
			if ir:
				ir.update({
					'res_model':'account.move',
					'res_id': valus,
					})
			ida = self.env['account.move'].search([('id','=',valus)])
			ida.attachment_ids = [(4, 0, [ir])]
		else:
			return False

	def unlink(self):
		for rec in self:
			if rec.state not in ['draft','cancel']:
				raise UserError(('You cannot delete an Timesheet which is not draft or cancelled.'))
		return super(TimeSheetDetailsKeffah, self).unlink()

	def push_time_sheet_info(self):
		for rec in self:
			for line in rec.project_id:
				line.write({'sheet_ids':[ (0,0,{
					'data_request':rec.data_request,
					'split':rec.split,
					'ot_line_subtotal':rec.ot_line_subtotal,
					'salary_line_subtotal':rec.salary_line_subtotal,
					'ot_salary_subtotal':rec.ot_salary_subtotal,
					})for rec in self]})
				
	def git_ot_info(self):
		product = []
		records = []
		test = []
		
		for rec in self:
			for line in rec.timesheet_order_ids:
				product.append(line.all_keffah_line_ids.product_template_id.id)
		salla = set(product)
		for data in salla:
			line_ot = self.env['time.sheet.ot.line'].search([('timesheet_ot_id','=',self.id)])
			products = self.env['product.product'].search([('id','=',data)])
			itmes = self.env['time.sheet.line'].search([('timesheet_id','=',self.timesheet_order_ids.timesheet_id.id),('all_keffah_line_ids.product_template_id','=',data)])
			ref = products.mapped('ot_ref')
			result = sum(itmes.filtered(lambda x: x.ot_hours > 0).mapped('ot_hours'))
			records.append((ref.id,result))

		for rec in records:
			if rec[1] > 0:
				self.timesheet_order_ot_ids = [(0,0,{
					'timesheet_ot_id':self.id,
					'job_position_id':rec[0],
					'ot':rec[1]
					})]

	def onchange_job_position_id(self):
		for rec in self.timesheet_order_ot_ids:
			if rec.job_position_id:
				rec.ot_price = rec.job_position_id.ot_price

class TimeSheetLine(models.Model):
	_name = 'time.sheet.line'

	timesheet_id = fields.Many2one('time.sheet.details',string='TimeSheet')
	timesheet_ot_id = fields.Many2one('time.sheet.details',string='TimeSheet')
	employee_id = fields.Many2one('hr.employee',string='Employee')
	department_id = fields.Many2one('department.line.keffah',string='Department')
	job_position_id = fields.Many2one('product.product',string='Job Position')
	all_keffah_line_ids = fields.Many2one('order.line.keffah',string="Job Position")
	working_hours_sheet = fields.Float(string="Standard Working Hours")
	unit_price = fields.Float(string="Unit Price")
	working_hours = fields.Float(string="Actual Working Hours")
	working_hours_month = fields.Float(string="Nunber Month")
	normal_working_hours = fields.Float(string="Normal Working Hours",readonly=True)

	ot_hours = fields.Float(string="OT Working Hours",readonly=True)

	identification_no = fields.Char(string='Identification No')
	salary =fields.Float(string='Salary',readonly=True)
	ot = fields.Float(string='OT')
	ot_percent = fields.Float(string="OT Percent",readonly=True)
	ot_price = fields.Float(string='OT Unit Price')
	ot_total = fields.Float(string="OT Salary",readonly=True)
	total = fields.Float(string="Total",readonly=True)


	@api.onchange('employee_id')
	def onchange_employee_id(self):

		all_keffah_line_ids = self.env['project.project'].search([('id','=',self.timesheet_id.project_id.id)]).mapped('staff_ids')	
		return {'domain': {'employee_id':[('id','in',all_keffah_line_ids.employee_id.ids)]}}

	def get_onchange_employee_id(self):
		all_keffah_line_ids = self.env['project.project'].search([('id','=',self.timesheet_id.project_id.id)]).mapped('staff_ids')	
		self.identification_no = self.employee_id.identification_id
		for rec in all_keffah_line_ids :
			if rec.identification_no == self.identification_no:
				self.all_keffah_line_ids = rec.all_keffah_line_ids.id
				self.department_id = rec.department_id.id

				self.unit_price = self.all_keffah_line_ids.price_unit

		self.normal_working_hours = self.all_keffah_line_ids.working_hours.hours

	def onchange_working_hours(self):
		product =[]
		result = []
		order_line_kefah = self.env['order.line.keffah'].search([('project_order_id.state','=','run')])
		itmes = self.env['time.sheet.details'].search([('id','=',self.timesheet_id.id)]).mapped('timesheet_order_ids')
		if self.working_hours:
			self.working_hours_sheet = self.normal_working_hours * self.working_hours_month
			self.salary = self.working_hours * self.unit_price
		self.ot_price = self.all_keffah_line_ids.product_template_id.ot_ref.list_price

		for rec in order_line_kefah:
			if self.all_keffah_line_ids.id == rec.id:
				self.ot_total = self.ot * self.ot_price

		self.total = self.salary + self.ot_total
		
	@api.onchange('ot_price')
	def onchange_ot_price(self):
		
		self.ot_total = self.ot_price * self.ot
	
class TimeSheetOtLine(models.Model):
	_name = 'time.sheet.ot.line'

	timesheet_ot_id = fields.Many2one('time.sheet.details',string='TimeSheet')
	all_keffah_line_ids = fields.Many2one('order.line.keffah',string="Job Position")
	job_position_id = fields.Many2one('product.product',string='OT Job Position')

	ot = fields.Float(string='OT')
	ot_price = fields.Float(string='OT Unit Price')
	ot_total = fields.Float(string="OT Salary",readonly=True)

	@api.onchange('ot_price')
	def onchange_ot_price(self):
		if self.ot_price:
			self.ot_total = self.ot_price * self.ot


class HolidayTimeSheet(models.Model):
	_name = 'holiday.time.sheet'

	name = fields.Char(string='Holiday TimeSheet')
	holiday_id = fields.Integer(string='Is Sheet',default=True)
	