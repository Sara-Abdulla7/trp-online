# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date

class TransferEmployee(models.Model):
	_name = 'transfer.employee'
	_description = 'Transfer Employee'
	_rec_name = 'project_id'
	_order = 'id desc'

	reference = fields.Char(string="Reference")
	date = fields.Date(string="Effective Date",default=fields.Datetime.now)
	project_id = fields.Many2one('project.project',string='Project Name')
	project_id_to = fields.Many2one('project.project',string='To Project')
	transfer_type = fields.Selection([('internal_transfer','Internal Transfer'),('out_transfert','Out Transfer')],string='Type Transfer')

	company_id = fields.Many2one('res.company',string="Company",default=lambda self: self.env.user.company_id)
	user_id = fields.Many2one('res.users',string="User",default=lambda self: self.env.user)
	state = fields.Selection([
		('draft', 'Draft'),
		('confirm', 'Confirmed'),
		('done', 'Transfer Completed'),
	], string='Status',
		track_visibility='onchange', help='Status of the Transfer Employee', default='draft')

	transfer_ids = fields.One2many('transfer.employee.line','transfer_line_id',string="Transfer Line")

	@api.onchange('project_id')
	def onchange_project_no(self):
		if self.project_id:
			obj = self.env['project.project'].search([('id','!=',self.project_id.id)])
			return{'domain': {'project_id_to':[('id','in',obj.ids)]}}

	@api.onchange('project_id_to')
	def onchange_project_to_no(self):
		if self.project_id_to:
			obj = self.env['project.project'].search([('id','!=',self.project_id_to.id)])
			return{'domain': {'project_id':[('id','in',obj.ids)]}}

	def action_confirm(self):
		for rec in self:
			rec.state = 'confirm'

	def action_Done(self):
		for rec in self:
			if self.transfer_type == 'internal_transfer': 
				self.action_transfer_internal()
				rec.state = 'done'
			else:
				self.action_transfer_outernal()
				rec.state='done'

	def action_transfer_internal(self):
		for rec in self:
			if rec.transfer_type == "internal_transfer":
				for line in rec.transfer_ids:
					order = self.env['project.project'].search([('id','=',rec.project_id.id)]).mapped('order_ids')
					project = self.env['project.project'].search([('id','=',rec.project_id.id),('name','=',rec.project_id.name)]).mapped('staff_ids')
					obj = project.filtered(lambda r:r.employee_id == line.employee_id  or r.identification_no == line.identification_no)
					if obj:
						for vals in obj:		
							if line.new_position_id:
								data = order.filtered(lambda r:r.product_template_id.id == line.new_position_id.id).id
								vals.update({
									'all_keffah_line_ids':data,
									})	
							if line.new_department_id:
								vals.update({
									'department_id':line.new_department_id.id,
									})
							if line.new_working_hours:
								vals.update({
									'working_hours':line.new_working_hours,
									})
					emp = self.env['transfer.details'].search([('project_id','=',rec.project_id.id),('employee_id','=',obj.employee_id.id)])
					if emp:
						for vals in emp:
							if line.new_position_id:
								vals.update({
									'job_id':line.new_position_id.id,
									})
							
							if line.new_department_id:
								vals.update({
									'department_id':line.new_department_id.id,
									})

							if line.new_working_hours:
								vals.update({
									'hours_work':line.new_working_hours,
									})

	def action_transfer_outernal(self):
		emp_out = {}
		emp_id=[]
		if self.transfer_type == 'out_transfert':
			for rec in self:
				for line in rec.transfer_ids:
					order = self.env['project.project'].search([('id','=',rec.project_id_to.id)]).mapped('order_ids')
					project = self.env['project.project'].search([('id','=',rec.project_id.id),('name','=',rec.project_id.name)]).mapped('staff_ids')
					obj = project.filtered(lambda r:r.employee_id == line.employee_id  or r.identification_no == line.identification_no)
					if obj:
						a1 = line.employee_id.id
						a2 = line.identification_no
						id_of_position = "test"
						id_of_department = "test"
						hours_of_working = 0

						if line.new_position_id:
							data = order.filtered(lambda r:r.product_template_id.id == line.new_position_id.id).id
							id_of_position=line.new_position_id.id
						else:
							id_of_position=line.old_position_id.id

						if line.new_department_id:
							id_of_department=line.new_department_id.id

						else:
							id_of_department=line.old_department_id.id

						if line.new_working_hours:
							hours_of_working=line.new_working_hours
						else:
							hours_of_working=line.old_eworking_hours

						project_tow = self.env['project.project'].search([('id', '=', self.project_id_to.id)])
						for vals in project_tow:
							self.env['old.salary'].create({
								'project_id':self.project_id.id,
								'project_id_to':self.project_id_to.id,
                        		'employee_id':line.employee_id.id,
					   			'old_department_id':line.old_department_id.id,
					   			'old_working_hours':line.old_eworking_hours,
					   			'active':True,
				    				})	
							if vals.state == 'run' :
								project_tow.update({'staff_ids':[ (0,0,{
									'project_id':project_tow,
	                	        	'employee_id':line.employee_id.id,
							    	'identification_no':line.identification_no,
						    		'all_keffah_line_ids':data,
						    		'department_id':id_of_department,
							    	'working_hours':hours_of_working,
							    	'laborer_status':'working',
	                        		})]
								})
								self.env['transfer.details'].create({
									'project_id':self.project_id_to.id,
                        			'employee_id':line.employee_id.id,
					    			'identification_no':line.identification_no,
					    			'job_id':id_of_position,
					    			'department_id':id_of_department,
					    			'hours_work':hours_of_working,
					    			'state':'working',
				    				})							
							elif vals.state == 'draft' or vals.state == 'confirm':
								project_tow.update({'staff_ids':[ (0,0,{
									'project_id':project_tow,
	                	        	'employee_id':line.employee_id.id,
							    	'identification_no':line.identification_no,
						    		'all_keffah_line_ids':data,
						    		'department_id':id_of_department,
							    	'working_hours':hours_of_working,
							    	'laborer_status':'ready',
	                        		})]
								})	
							else:
								project_tow.update({'staff_ids':[ (0,0,{
									'project_id':project_tow,
	                	        	'employee_id':line.employee_id.id,
							    	'identification_no':line.identification_no,
						    		'all_keffah_line_ids':data,
						    		'department_id':id_of_department,
							    	'working_hours':hours_of_working,
							    	'laborer_status':'not_working',
	                        		})]
								})
						obj.unlink()

						project_detail_unlink = self.env['transfer.details'].search([('project_id','=',self.project_id.id)])
						for detail in project_detail_unlink:
							if detail.employee_id == line.employee_id and detail.all_keffah_line_ids == line.old_all_keffah_line_ids and detail.department_id == line.old_department_id and detail.hours_work == line.old_eworking_hours:
								detail.unlink()


						hr_holiday = self.env['hr.employee'].search([('laborer_status','=','holiday')])
						project_holiday = self.env['project.project'].search([('id','=',self.project_id_to.id)]).mapped('staff_ids')
						transfer_detail_holiday = self.env['transfer.details'].search([('project_id','=',self.project_id_to.id)])
						for vals in hr_holiday:
							for val in project_holiday:
								if vals.id == val.employee_id.id:
									val.laborer_status = 'holiday'

							for val in transfer_detail_holiday:
								if vals.id == val.employee_id.id:
									val.state = 'holiday'

class TransferEmployeeLine(models.Model):
	_name = 'transfer.employee.line'

	transfer_line_id = fields.Many2one('transfer.employee',string='Transfer')
	identification_no = fields.Char(string='Identification No')
	employee_id = fields.Many2one('hr.employee',string='Laborers',readonly=True)

	old_position_id = fields.Many2one('product.product',string='Job Position',readonly=True)
	new_position_id = fields.Many2one('product.product', string='New Job Position')
	test_ids=fields.Many2many('department.line.keffah',compute='department_domain')

	old_all_keffah_line_ids = fields.Many2one('order.line.keffah',string="Job Position")
	new_all_keffah_line_ids = fields.Many2one('order.line.keffah',string="Job Position")

	old_department_id = fields.Many2one('department.line.keffah',string='Old Department',readonly=True)
	new_department_id = fields.Many2one('department.line.keffah',string='New Department')

	old_eworking_hours = fields.Float(string="Old Working Hours ")
	new_working_hours = fields.Float(string="New Working Hours")
	test_ids=fields.Many2many('department.line.keffah',compute='department_domain')
	job_ids=fields.Many2many('product.product',compute='job_domain')


	@api.onchange('new_department_id')
	@api.depends('new_department_id')
	def department_domain(self):
		if self.transfer_line_id.transfer_type == 'internal_transfer':
			department_obj = self.env['department.department.keffah'].search([('company_name_id.id','=',self.transfer_line_id.project_id.id)]).mapped('department_ids')
			for rec in self:
				rec.test_ids=[(6,0,department_obj.ids)]
		else:
			department_obj = self.env['department.department.keffah'].search([('company_name_id.id','=',self.transfer_line_id.project_id_to.id)]).mapped('department_ids')
			for rec in self:
				rec.test_ids=[(6,0,department_obj.ids)]



	@api.onchange('new_position_id')
	@api.depends('new_position_id')
	def job_domain(self):
		if self.transfer_line_id.transfer_type == 'internal_transfer':
			job = self.env['project.project'].search([('id','=',self.transfer_line_id.project_id.id)]).mapped('order_ids.product_template_id')
			for rec in self:
				rec.job_ids=[(6,0,job.ids)]
		else:
			job = self.env['project.project'].search([('id','=',self.transfer_line_id.project_id_to.id)]).mapped('order_ids.product_template_id')
			for rec in self:
				rec.job_ids=[(6,0,job.ids)]
		

class TransferDetails(models.Model):
	_name = 'transfer.details'
	_description = "Transfer Details"
	_rec_name = 'employee_id'

	project_id = fields.Many2one('project.project',string="Project")
	identification_no = fields.Char(string='Identification No')
	employee_id = fields.Many2one('hr.employee',string='Employee')
	department_id = fields.Many2one('department.line.keffah',string="Department")
	job_id = fields.Many2one('product.product', string="Job")
	all_keffah_line_ids = fields.Many2one('order.line.keffah',string="Job Position")
	hours_work = fields.Float('Hours work')
	project_staff_id = fields.Many2one('project.staff',string="project staff")
	state = fields.Selection([('working', 'Working'),('not_working','Not Working'),('ready', 'Ready'),('out of service', 'Out Of Service'),('holiday','Holiday'),],string="Employee Statue")