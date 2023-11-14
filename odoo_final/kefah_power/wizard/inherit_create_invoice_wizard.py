from odoo import fields, models,api, _
from odoo.tools import float_is_zero
import time

class Sale_advance_payment_inv(models.TransientModel):
	_inherit='sale.advance.payment.inv'

	is_man_power_order = fields.Boolean(readonly=True)


	def default_get(self, fields_list):
		res = super().default_get(fields_list)
		if self.is_man_power_order == True:
			res['advance_payment_method'] = 'fixed'
		else:
			res['advance_payment_method'] = 'delivered'
		return res

	@api.onchange('is_man_power_order')
	def _get_is_man_power(self):

		if self.is_man_power_order == True:
			self.advance_payment_method = 'fixed'
		else:
			self.advance_payment_method = 'delivered'


