from odoo import models, fields, api


class Account_account(models.Model):
	_inherit = 'account.account'

	company_boolean= fields.Boolean(related='company_id.is_man_power')
	analytic_boolean= fields.Boolean(string="Analytic Check")



class Account_move_line(models.Model):
	_inherit = 'account.move.line'

	analytic_boolean= fields.Boolean(related='account_id.analytic_boolean')

