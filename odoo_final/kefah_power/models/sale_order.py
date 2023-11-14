# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.addons.payment import utils as payment_utils
from odoo.fields import Command

class SaleOrderKeffah(models.Model):
    _inherit = 'sale.order'

    s_type = fields.Selection([('new_invoice', 'New Quotations '),('resale', 'Resale Quotations')], string='Sale Type', help='Sale Type')
    is_resale = fields.Boolean(string="is_resale",readonly=True)
    resale_types = fields.Selection([('resale', 'Create a New Service'),('resale_2', 'Add On Old Service')], string='Resale Type',track_visibility='onchange', help='Employee Type', required='True')
    is_man_power = fields.Boolean(related="company_id.is_man_power", readonly=True)
    is_man_power_order = fields.Boolean(string="Is Man Power Order")
    sa_vat = fields.Char(related="partner_id.vat", readonly=True)
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    product_categ_ids = fields.Many2many('product.category',string='Product Category')
    is_check = fields.Boolean(string='Is Check', related="company_id.is_man_power", readonly=True)
    hide_unit_price = fields.Boolean(string="Hide Unit Price", help="Hide unit price in the printed PDF.")
    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True,
                                     readonly=True, compute='_amount_all',
                                     track_visibility='always')
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True,
                                 compute='_amount_all',
                                 track_visibility='always')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True,
                                   compute='_amount_all',
                                   track_visibility='always')
    sales_order_id = fields.Many2one('sale.order', string="Sale Order")
    date = fields.Datetime(related="sales_order_id.date_order",string="Date")

    amount_limit_status = fields.Selection([('warning', 'Warning '),('amount_available', 'Amount Available')], string='Amount Limit',default='amount_available')   


    amount_limit_status = fields.Selection([('warning', 'Warning '),('amount_available', 'Amount Available')], string='Amount Limit',default='amount_available')   


    total_down_payment = fields.Monetary(string="Total Down Payment",readonly=True)
    down_payment_compute = fields.Monetary(readonly=True ,compute="_down_payment_compute",string='Total down payment compute')
    total_minus_down_payment = fields.Monetary(string="Total Minus Down Payment",readonly=True)
    total_invoice_compute = fields.Integer(readonly=True ,compute="_total_invoice_compute",string='Total invoices compute')

    # account_order_id = fields.One2many('account.move',string='order_id')

    @api.onchange('company_id')
    def onchange_cat_company(self):
        cat_obj = self.env['product.category'].search([('company_id','=',self.company_id.id)])
        return{'domain': {'product_categ_ids':[('id','in',cat_obj.ids)]}}


    @api.depends('order_line.price_total')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = amount_discount = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax,
            })


    @api.onchange('partner_id')
    def get_partner(self):
        if self.partner_id:
            self.is_man_power_order = False
    
   
    def _prepare_invoice(self):
        record = super(SaleOrderKeffah, self)._prepare_invoice()
        if self.is_man_power_order == False:
            return record
        else:
            record['sale_orders_id'] = self.id
            record['is_man_power_order'] = True
            return record


    @api.onchange('partner_id')
    def onchange_sale_order(self):
        order = self.env['sale.order'].search([('partner_id', '=', self.partner_id.id),('s_type','=','new_invoice'),('state', '=','sale'),('is_man_power_order','=',True)])
        return{'domain':{'sales_order_id':[('id','in',order.ids)]}}

    def resale_order(self):
        SO = self.name
        for rec in self:
            if rec.s_type == 'resale' and rec.is_man_power_order == True:
                obj = rec.env['sale.order'].search([('id','=',rec.sales_order_id.id)])
                obj.update({'order_line':[ (0,0,{
                        'order_id':obj.id,
                        'display_type': 'line_section',
                        'name': _("New Sale Order ({0})".format(SO)),
                        })]
                    })
                obj.update({'order_line':[ (0,0,{
                        'order_id':obj.id,
                        'product_template_id':line.product_template_id.id,
                        'product_id':line.product_id.id,
                        'name':line.name,
                        'working_days':line.working_days.id,
                        'working_hours':line.working_hours.id,
                        'working_month':line.working_month.id,
                        'product_uom_qty':line.product_uom_qty,
                        'price_unit':line.price_unit,
                        'tax_id':line.tax_id,
                        'total_add_monthly':line.total_add_monthly,
                        'price_subtotal':line.price_subtotal,
                        })for line in rec.order_line]
                    })

    def project_order_ids(self):
        for rec in self:
            if rec.s_type == 'resale' and rec.is_man_power_order == True:
                obj2 = self.env['project.project'].search([('sale_order_project_id','=',self.sales_order_id.id)])
                obj3 = obj2.mapped('order_ids')
                x=[]
                for val in obj2:
                    if rec.resale_types == 'resale_2':
                        for line in rec.order_line:
                            if line.product_id.id in obj2.order_ids.product_template_id.ids:
                                for vals in val.order_ids:
                                    if line.product_id == vals.product_template_id:
                                        qty = line.product_uom_qty
                                        vals.quantity += qty 
                                        vals.quantity -= qty 
                            if line.product_id.id not in obj2.order_ids.product_template_id.ids:
                                obj2.update({'order_ids':[(0,0,{
                                    'product_template_id':line.product_id.id,
                                    'working_days':line.working_days.id,
                                    'working_hours':line.working_hours.id,
                                    'quantity':line.product_uom_qty - line.product_uom_qty,
                                    'price_unit':line.price_unit,
                                    'total_monthly':line.total_monthly,
                                    'working_month':line.working_month.id,
                                    'price_subtotal':line.price_subtotal
                                    })]
                                })
                    else:
                        for line in rec.order_line:
                            if line.product_id.id in obj2.order_ids.product_template_id.ids:
                                obj2.update({'order_ids':[(0,0,{
                                'resale':"RE",
                                'product_template_id':line.product_id.id,
                                'working_days':line.working_days.id,
                                'working_hours':line.working_hours.id,
                                'quantity':line.product_uom_qty,
                                'price_unit':line.price_unit,
                                'total_monthly':line.total_monthly,
                                'working_month':line.working_month.id,
                                'price_subtotal':line.price_subtotal
                                })]})

                        for line in rec.order_line:
                            if line.product_id.id not in obj2.order_ids.product_template_id.ids:
                                obj2.update({'order_ids':[(0,0,{
                                'product_template_id':line.product_id.id,
                                'working_days':line.working_days.id,
                                'working_hours':line.working_hours.id,
                                'quantity':line.product_uom_qty,
                                'price_unit':line.price_unit,
                                'total_monthly':line.total_monthly,
                                'working_month':line.working_month.id,
                                'price_subtotal':line.price_subtotal
                                })]
                                })
                                
    @api.onchange('s_type')
    def onchange_is_resale(self):
        if self.s_type == "resale":
            self.is_resale = True
        else:
            self.is_resale = False


    @api.depends('order_line.price_subtotal', 'order_line.price_tax','order_line.price_total')
    def _compute_amounts(self):
        """Compute the total amounts of the SO."""
        check = super(SaleOrderKeffah, self)._compute_amounts()
        for order in self:
            order_lines = order.order_line.filtered(
                lambda x: not x.display_type)
            order.amount_untaxed = sum(order_lines.mapped('price_subtotal'))
            order.amount_tax = sum(order_lines.mapped('price_tax'))
            order.tax_totals = order.amount_total
        return check

    @api.depends('order_line.tax_id', 'order_line.price_unit', 'amount_total',
                 'amount_untaxed', 'currency_id')
    def _compute_tax_totals(self):
        for order in self:
            order_lines = order.order_line.filtered(
                lambda x: not x.display_type)
            order.tax_totals = self.env['account.tax']._prepare_tax_totals(
                [x._convert_to_tax_base_line_dict() for x in order_lines],
                order.currency_id or order.company_id.currency_id,
            )

    def action_confirm(self):
        res = super(SaleOrderKeffah,self).action_confirm()
        self.resale_order()
        self.project_order_ids()
        if self.is_man_power_order == True and self.s_type != 'resale':
            return {
            'name': _('Create Project'),
            'type': 'ir.actions.act_window',
            'view_type':'form',
            'view_mode':'form',
            'res_model':'sale.wizard',
            'target': 'new',
            'context': {
                'default_partner_id':self.partner_id.id,
                'default_date_start': self.date_order,
                'default_company_id': self.company_id.id,
                'default_subtotal':self.amount_untaxed,
                'default_sale_order_id':self.id,
                }
            }
        else:
            return False
        return res


        # ====================================================================== #


    def _prepare_invoice(self):
       res = super(SaleOrderKeffah,self)._prepare_invoice()
       res['sale_orders_id'] = self.id
       return res


    def _total_invoice_compute(self):
        sale_orders_ids = self.env['account.move'].search([('sale_orders_id','=',self.id)])

        self.total_invoice_compute = len(sale_orders_ids)


    def action_view_invoice_button(self):
        sale_orders_ids = self.env['account.move'].search([('sale_orders_id','=',self.id)])
        action = self.env['ir.actions.actions']._for_xml_id('account.action_move_out_invoice_type')

        if len(sale_orders_ids) > 1:
            action['domain'] = [('id', 'in', sale_orders_ids.ids)]
        elif len(sale_orders_ids) == 1:
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = sale_orders_ids.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        context = {
            'default_move_type': 'out_invoice',
        }
        if len(self) == 1:
            context.update({
                'default_partner_id': self.partner_id.id,
                'default_partner_shipping_id': self.partner_shipping_id.id,
                'default_invoice_payment_term_id': self.payment_term_id.id or self.partner_id.property_payment_term_id.id or self.env['account.move'].default_get(['invoice_payment_term_id']).get('invoice_payment_term_id'),
                'default_invoice_origin': self.name,
                'default_user_id': self.user_id.id,
            })
        action['context'] = context
        return action

    def _down_payment_compute(self):
        self.down_payment_compute = 0
        for rec in self.order_line:
            if rec.is_downpayment == True:
                self.down_payment_compute += rec.price_unit
        self.total_down_payment = self.down_payment_compute
        self.total_minus_down_payment = self.amount_total - self.total_down_payment


        if self.total_minus_down_payment < 0 :
            self.amount_limit_status = 'warning'
        else:
            self.amount_limit_status = 'amount_available' 



class WorkDay(models.Model):
    _name = 'work.day'
    _description = 'work day'

    day = fields.Integer(string='Day')
    labels = fields.Many2one('day.label', string='Name Day')

    @api.depends('day','labels')
    def name_get(self):
        res = []
        for record in self:
            name = record.day
            if record.labels:
                data =  str(name) + ' ' + record.labels.name
            res.append((record.id, data))
        return res

class labelDay(models.Model):
    _name = 'day.label'
    _description = 'day label'

    name = fields.Char(string='Name')

class WorkHours(models.Model):
    _name = 'work.hours'
    _description = 'work hours'


    hours = fields.Integer(string='Hour')
    labels = fields.Many2one('label.label', string='Name Hour')

    @api.depends('hours','labels')
    def name_get(self):
        res = []
        for record in self:
            name = record.hours
            if record.labels:
                data =  str(name) + ' ' + record.labels.name
            res.append((record.id, data))
        return res

class label(models.Model):
    _name = 'label.label'
    _description = 'label'

    name = fields.Char(string='Name')


class WorkMonthly(models.Model):
    _name = 'work.monthly'
    _description = 'work monthly'


    monthly = fields.Integer(string='Month')
    labels = fields.Many2one('month.month', string='Name Month')

    @api.depends('monthly','labels')
    def name_get(self):
        res = []
        for record in self:
            name = record.monthly
            if record.labels:
                data =  str(name) + ' ' + record.labels.name
            res.append((record.id, data))
        return res


class Month(models.Model):
    _name = 'month.month'
    _description = 'Month'

    name = fields.Char(string='Name')

class SaleOrderLineKeffah(models.Model):
    _name = 'sale.order.line'
    _inherit = 'sale.order.line'

    working_days = fields.Many2one('work.day',string="Working Days")
    working_hours = fields.Many2one('work.hours',string="Working Hours")
    monthly_hours = fields.Float(string="Monthly Hours", compute="_compute_monthly_hours_rate", store=True)
    month_rate = fields.Float(string="Monthly Rate", compute="_compute_monthly_hours_rate", store=True)
    total_monthly = fields.Float(string="Total Monthly", compute="_compute_monthly_hours_rate", store=True)
    working_month = fields.Many2one('work.monthly',string="Monthly Working Period")
    total_add_monthly = fields.Float(string="Total Monthly Period")
    is_man_power_order = fields.Boolean(string="Is Man Power Order?",compute="_onchange_is_man_power_order",store=True)


    @api.depends('order_id.is_man_power_order')
    def _onchange_is_man_power_order(self):
        for rec in self:
            if rec.order_id.is_man_power_order == True:
                rec.is_man_power_order = True
            else:
                return False

    @api.onchange('product_template_id')
    def onchange_product_no_man_power(self):
        if self.order_id.is_man_power_order != True:
            products = self.env['product.template'].search([('is_man_power', '=', False)])
            return{'domain': {'product_template_id':[('id','in',products.ids),('is_ot','=',False)]}}



    @api.onchange('product_template_id')
    def onchange_product_cat(self):
        if self.order_id.is_man_power_order == True:
            record =  self.order_id.product_categ_ids.ids
            category_obj = self.env['product.category'].search([('id','in',[rec for rec in record])])
            products = self.env['product.template'].search([('categ_id.id','in',[rec.id for rec in category_obj])])
            return{'domain': {'product_template_id':[('id','in',products.ids),('is_ot','=',False)]}}
        else:
            return False


    """@api.depends() should contain all fields that will be used in the calculations"""
    @api.depends('working_days', 'working_hours', 'product_uom_qty', 'price_unit','total_add_monthly','working_month')
    def _compute_monthly_hours_rate(self):
            for rec in self:
                if rec.order_id.is_man_power_order == True:
                    rec.monthly_hours = rec.working_days.day * rec.working_hours.hours
                    rec.month_rate = rec.monthly_hours * rec.price_unit
                    rec.total_monthly = rec.month_rate * rec.product_uom_qty
                else:
                    return False

    @api.onchange('working_month')
    def _onchange_total_month(self):
        for rec in self:
            if rec.order_id.is_man_power_order == True:
                rec.update({'total_add_monthly': rec.total_monthly * rec.working_month.monthly})


    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id','total_add_monthly','working_days','working_hours')
    def _compute_amount(self):
        super (SaleOrderLineKeffah,self)._compute_amount()
        for line in self:
            if not line.order_id.is_man_power_order:
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                            product=line.product_id, partner=line.order_id.partner_shipping_id)
            else:
                if line.product_uom_qty:
                    price = (line.total_add_monthly / line.product_uom_qty) * (1 - (line.discount or 0.0) / 100.0)
                else:
                    price = line.total_add_monthly * (1 - (line.discount or 0.0) / 100.0)

                taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                            product=line.product_id, partner=line.order_id.partner_shipping_id)
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })





    





