# -*- coding: utf-8 -*-
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo import models, fields, api


class SelectProducts(models.TransientModel):

    _name = 'select.products'
    _description = 'Select Products'

    transfer_id = fields.Many2one('transfer.employee', string='Transfer',readonly=True)
    product_ids = fields.Many2many('transfer.details', string='Products')

    @api.onchange('product_ids')
    def onchange_department(self):
        department_obj = self.env['transfer.details'].search([('project_id','=',self.transfer_id.project_id.id)])
        if self.product_ids:
            return{'domain': {'product_ids':[('id','in',department_obj.ids)]}}
        return{'domain': {'product_ids':[('id','in',department_obj.ids)]}}


    def select_products(self):
        transfer_id = self.env['transfer.employee'].browse(self._context.get('active_id', False))
        for product in self.product_ids:
            self.env['transfer.employee.line'].create({
                'transfer_line_id':transfer_id.id,
                'identification_no':product.identification_no,
                'employee_id':product.employee_id.id,
                'old_position_id':product.job_id.id,
                'old_department_id':product.department_id.id,
                'old_eworking_hours':product.hours_work,
                })
