from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    leads_per_day = fields.Integer(string="Leads per Day", config_parameter='crm_leads.leads_per_day')
    number_of_days = fields.Integer(string="Number Of Days", config_parameter='crm_leads.number_of_days')
    datetime_of_warning_day = fields.Datetime(string="DateTime Of Warning Day", config_parameter='crm_leads.datetime_of_warning_day')
    date_of_warning_month = fields.Datetime(string="Date Of Warning Month", config_parameter='crm_leads.date_of_warning_month')
