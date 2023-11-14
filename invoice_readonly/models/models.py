from odoo import models, fields, api


class invoice_readonly(models.Model):
	_inherit = 'account.move'
	check_label = fields.Boolean(string="Check Label")
	id_invoice_lines = fields.Many2one('account.move.line',string="Invoice Lines",domain="[('move_id','=',id)]")
	label_name = fields.Char(string="Label")



	def default_get(self, fields_list):

		res = super().default_get(fields_list)

		if self.check_label == True:
			self.check_label = False

		return res

	@api.onchange('check_label')
	def check_label_line(self):
		line = self.env['account.move'].search([('id','=',self._origin.id)]).mapped('invoice_line_ids')
		return{'domain':{'id_invoice_lines':[('id','in',line.ids)]}}

	@api.onchange('id_invoice_lines','check_label')
	def change_label_name(self):
		self.label_name = False

	@api.onchange('label_name')
	def change_label_name_line(self):
		if self.label_name != False:		
			self.id_invoice_lines.name = self.label_name
