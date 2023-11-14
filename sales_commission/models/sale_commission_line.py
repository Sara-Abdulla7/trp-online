from odoo import models, fields, api


class SaleCommissionLine(models.Model):
    _name = 'sale.commission.line'
    _description = 'Sale Commission Line'

    name = fields.Many2one('res.users', string='Employee Name')
    sale_commission_id = fields.Many2one('sale.commission', string='Commission')
    target = fields.Float()
    state = fields.Selection([('success', 'Success'), ('failure', 'Failure')], default=False)
    commission_type = fields.Selection(related='sale_commission_id.commission_type', store=True)
    commission_type_round = fields.Selection(related='sale_commission_id.commission_type_round', store=True)
    commission_rate = fields.Float(string='Commission Rate')
    commission_done = fields.Boolean()
