from odoo import models, fields, api, _


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    commission_amount = fields.Float(compute='compute_sale_commission_for_salesperson')
    total_commission_amount = fields.Float(compute='compute_sale_commission_for_salesperson')

    def compute_sale_commission_for_salesperson(self):
        for rec in self:
            commission = rec.env['sale.commission.line'].search(
                [('name', '=', rec.user_id.id), ('state', '=', 'success')])
            rec.commission_amount = sum([x.commission_rate for x in commission if x.commission_done == False])
            rec.total_commission_amount = sum([x.commission_rate for x in commission ])

    # smart button
    def action_open_sale_commission(self):
        return {
            'name': _(self.name),
            'res_model': 'sale.commission.line',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'target': 'current',
            'nodestroy': True,
            'domain': [('name.id', '=', self.user_id.id), ('commission_done', '=', False)],
        }

    def action_open_total_commission_amount(self):
        return {
            'name': _(self.name),
            'res_model': 'sale.commission.line',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'target': 'current',
            'nodestroy': True,
            'domain': [('name.id', '=', self.user_id.id)],
        }
