
import time
from dateutil.relativedelta import relativedelta
from odoo import fields, models,api,_
from odoo.exceptions import UserError


class SaleWizard(models.TransientModel):
    _name = 'sale.wizard'
    _description = 'Create Project From Sale If Client Need Man Power'

    partner_id = fields.Many2one('res.partner',string='Partner',readonly=True)
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    company_id = fields.Many2one('res.company',string='Company',readonly=True)
    subtotal = fields.Float(string='Subtotal')
    analytic_id = fields.Many2one('account.analytic.account',string='Analytic Account',readonly=True)
    sale_order_id = fields.Many2one('sale.order', string="Sale Order ",readonly=True)

    warning = fields.Char(string="Warning",readonly=True,default='Warning: this Customer is already have a project.')
    is_customer_check = fields.Boolean()

    def create_project(self):
        obj = self.env['sale.order'].search([('id','=',self.sale_order_id.id)])
        for record in self:
            project = self.env['project.project'].create({
                'name':record.partner_id.name,
                'project_income':record.subtotal,
                'analytic_account_id':record.analytic_id.id,
                'sale_order_project_id':record.sale_order_id.id,
                })
            project.write({'order_ids' : [ (0,0,
                {'product_template_id':line.product_id.id,
                 'working_days':line.working_days.id,   
                 'working_hours':line.working_hours.id,
                 'quantity':line.product_uom_qty,
                 'price_unit': line.price_unit,
                 'total_monthly': line.total_monthly,
                 'working_month': line.working_month.id,
                 'price_subtotal': line.price_subtotal
                 })for line in obj.order_line]})


    @api.onchange('partner_id')
    def onchange_partner_id(self):
        project_id= self.env['project.project'].search([('partner_id','=',self.partner_id.id)]).mapped('partner_id')
        for rec in project_id:
            self.is_customer_check = True


    # def default_get(self, fields_list):
    #     res = super().default_get(fields_list)
    #     project_id= self.env['project.project'].search([('partner_id','=',self.partner_id)]).mapped('partner_id')
    #     print(project_id)
    #     for rec in self:

    #         if rec == self.partner_id:
    #             res['warning'] = 'this Customer is already in have a project.'
    #             self.is_customer_check_compute = 1
    #         else:
    #             res['warning'] = 'none.'
    #     return res

        # if self.is_man_power_order == True:
        #     res['advance_payment_method'] = 'fixed'
        # else:
        #     res['advance_payment_method'] = 'delivered'
        # return res

    # def _check_customer(self):
    #     project_id= self.env['project.project'].search([('partner_id','=',self.partner_id.id)])
    #     print(project_id)
    #     for rec in project_id:
    #         self.is_customer_check_compute = 1
    #         self.warning ="this Customer is already in have a project."
