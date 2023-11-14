from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleCommission(models.Model):
    _name = 'sale.commission'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Sales Commission'

    name = fields.Char(string='Name')
    active = fields.Boolean('Active', default=True, tracking=True)
    sales_person_id = fields.Many2many('res.users', string='SalesPerson')
    commission_rate = fields.Float(string='Commission Rate')
    commission_rate_percentage = fields.Float(string="Percentage Rate", digits=(16, 1))
    commission_type = fields.Selection([('fixed', 'Fixed (sale order)'), ('percentage', 'Percentage (Invoice)')],
                                       string='Commission Type')
    commission_type_round = fields.Selection([('quarter', 'Quarter'), ('half_year', 'Half year'), ('year', 'Year')],
                                             string='Commission Type Round')
    sales_order_target = fields.Float(string='Sales Order Target')
    commission_line_count = fields.Integer(compute='compute_sale_commission_line_for_salesperson')
    commission_line_ids = fields.One2many('sale.commission.line', 'sale_commission_id')

    def compute_sale_order_commission(self):
        sales_commission_cron_job = self.env.ref('sales_commission.corn_job_sales_commission_for_fixed')
        lastcall = sales_commission_cron_job.lastcall
        nextcall=sales_commission_cron_job.nextcall
        sales_commission_fixed = self.search([('active', '=', True), ('commission_type', '=', 'fixed')])
        for line in sales_commission_fixed:
            for rec in line.sales_person_id:
                sale_orders = line.env['sale.order'].search(
                    [('state', '=', 'sale'), ('user_id', '=', rec.id), ('date_order', '>=', lastcall),
                     ('date_order', '<=', nextcall), ('commission_done', '!=', True)])
                sale_orders_amount = sum([rec.amount_total for rec in sale_orders])
                rec.env['sale.commission.line'].create({'name': rec.id, 'sale_commission_id': line.id,
                                                        'commission_type': 'fixed',
                                                        'target': line.sales_order_target,
                                                        'commission_rate': line.commission_rate if sale_orders_amount >= line.sales_order_target else 0,
                                                        'state': 'success' if sale_orders_amount >= line.sales_order_target else 'failure'})

            for sale in sale_orders:
                    sale.commission_done = True


    def compute_invoice_paid_commission(self):
        sales_commission_cron_job = self.env.ref('sales_commission.corn_job_sales_commission_for_invoiced')
        lastcall = sales_commission_cron_job.lastcall
        nextcall=sales_commission_cron_job.nextcall
        sales_commission_percentage = self.search([('active', '=', True), ('commission_type', '=', 'percentage')])
        for line in sales_commission_percentage:
            for rec in line.sales_person_id:
                invoice_paid = line.env['account.move'].search(
                    [('payment_state', '=', 'paid'), ('invoice_user_id', '=', rec.id), ('invoice_date', '>=', lastcall),
                     ('invoice_date', '<=', nextcall), ('commission_done', '!=', True)])
                invoice_paid_amount = sum([rec.amount_total for rec in invoice_paid])
                rec.env['sale.commission.line'].create({'name': rec.id, 'sale_commission_id': line.id,
                                                        'commission_type': 'percentage',
                                                        'commission_rate': (
                                                                                       invoice_paid_amount / 100.0) * line.commission_rate_percentage,
                                                        'state': 'success'})
                for inv in invoice_paid:
                    inv.commission_done = True

    # smart button
    def action_open_sale_commission_line(self):
        return {
            'name': _(self.name),
            'res_model': 'sale.commission.line',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'target': 'current',
            'nodestroy': True,
            'domain': [('sale_commission_id.id', '=', self.id)],
        }

    def compute_sale_commission_line_for_salesperson(self):
        for rec in self:
            rec.commission_line_count = len(rec.commission_line_ids) or 0

    def unlink(self):
        for rec in self:
            if len(rec.commission_line_ids):
                raise UserError(_("Can't Delete Commission with At least line "))

        return super(SaleCommission, self).unlink()



    @api.onchange('commission_rate_percentage')
    @api.constrains('commission_rate_percentage')
    def check_commission_percentage_rate(self):
        for rec in self:
            if rec.commission_rate_percentage < 0 or rec.commission_rate_percentage > 100:
                raise UserError(_('Value Of Percentage Rate between 0 ====> 100'))


    @api.onchange('sales_person_id')
    @api.constrains('sales_person_id')
    def check_salesperson(self):
        for rec in self:
            salesperson_ids = rec.search([('commission_type', '=', rec.commission_type), ('id', '!=', rec.id or 0)]).mapped(
                'sales_person_id').ids
            for line in rec.sales_person_id:
                print(line.id)
                if line.id in salesperson_ids:
                    raise UserError(_('SalesPerson {} Already Exist in Another Commission'.format(line.name)))

