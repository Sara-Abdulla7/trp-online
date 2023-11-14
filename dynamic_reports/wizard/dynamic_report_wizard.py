# -*- coding: utf-8 -*-


from odoo import models, fields, api
from odoo.exceptions import UserError


class DynamicReport(models.TransientModel):
    _name = 'dynamic.report'

    model_id = fields.Many2one('ir.model', string='Model', required=True, index=True, ondelete='cascade')
    report_id = fields.Many2one('ir.actions.report', string='Report', required=True, index=True, ondelete='cascade')
    # order_number = fields.Char(string='Order Number', required=False, help="Use Capital Alphabet")
    order_number = fields.Reference(selection='_select_target_model', string="Order Number")

    @api.model
    def _select_target_model(self):
        models = self.env['ir.model'].search([])
        return [(model.model, model.name) for model in models]

    @api.onchange('model_id')
    def onchange_model_id(self):
        reports = self.env['ir.actions.report'].search([('model', '=', self.model_id.model)])
        return {'domain': {'report_id': [('id', 'in', reports.ids)]}}

    # @api.onchange('model_id')
    # def onchange_product_variant_data(self):
    #     model_name = self.model_id.name
    #     for i in self:
    #         for data in i.model_name:
    #             for line in data:
    #                 self.update({
    #                     'order_number': line.order_number
    #                 })

    def generate_dynamic_report(self, data=None):
        model = self.model_id.model
        order_number = self.order_number
        if not order_number:
            raise UserError("Enter Order Number")
        template_name = self.report_id.report_name
        order = self.env[model].search([('name', '=', order_number.name)])
        report = self.env['ir.actions.report']._get_report_from_name(template_name)
        return report.report_action(order.id)
