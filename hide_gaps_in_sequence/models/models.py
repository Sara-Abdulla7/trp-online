# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class hide_gaps_in_sequence(models.Model):
#     _name = 'hide_gaps_in_sequence.hide_gaps_in_sequence'
#     _description = 'hide_gaps_in_sequence.hide_gaps_in_sequence'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
