from odoo import models, fields
from odoo.exceptions import ValidationError
import datetime


class CrmLead(models.Model):
    _inherit = "crm.lead"

    def get_crm_leads_salesperson_configuration(self):
        leads_per_day = self.env['ir.config_parameter'].sudo().get_param('crm_leads.leads_per_day')
        number_of_days = self.env['ir.config_parameter'].sudo().get_param('crm_leads.number_of_days')
        datetime_of_warning_day = self.env['ir.config_parameter'].sudo().get_param('crm_leads.datetime_of_warning_day')
        date_of_warning_month = self.env['ir.config_parameter'].sudo().get_param('crm_leads.date_of_warning_month')

        if not leads_per_day:
            raise ValidationError('Please Enter Leads Per Day')
        if not number_of_days:
            raise ValidationError('Please Enter Number Of Days For Leads')
        if not datetime_of_warning_day:
            raise ValidationError('Please Enter Datetime of Warning Day For Leads')
        if not date_of_warning_month:
            raise ValidationError('Please Enter date of Warning Month For Leads')
        return leads_per_day, number_of_days, datetime_of_warning_day, date_of_warning_month

    def warning_mail_day_for_lead(self):
        leads_per_day, number_of_days, *_ = self.get_crm_leads_salesperson_configuration()
        email_to, email_cc = self.get_crm_salesperson_email()
        salespersons = self.env['res.users'].search([('is_salesperson', '=', True)])
        day = datetime.datetime.now().date()
        d1 = datetime.datetime.strftime(day, "%Y-%m-%d %H:%M:%S")
        d2 = datetime.datetime.strftime(day, "%Y-%m-%d 23:59:59")
        for sales in salespersons:
            count_leads_per_day = self.search(
                [('user_id', '=', sales.id), ('create_date', '>=', d1), ('create_date', '<=', d2)])
            if len(count_leads_per_day) < int(leads_per_day):
                mail_template = self.env.ref('crm_leads.mail_template_warning_day_for_leads')
                if mail_template:
                    email_values = {
                        'email_to': (','.join(email_to+[sales.email])),
                        'email_cc': (','.join(email_cc+[sales.email])) or '',
                        'email_from': self.env.user.email,

                    }
                    ctx = {'salesperson_name': sales.name,
                           'day': fields.Date.today(),
                           'leads_per_day': leads_per_day,
                           'create_leads_per_day': len(count_leads_per_day)}
                    mail_template.with_context(**ctx).send_mail(self.id,
                                                                email_values=email_values,
                                                                force_send=True)

    def warning_mail_month_for_lead(self):
        leads_per_day, number_of_days, datetime_of_warning_day, date_of_warning_month = self.get_crm_leads_salesperson_configuration()
        email_to, email_cc = self.get_crm_salesperson_email()

        leads_per_month = int(leads_per_day) * int(number_of_days)
        salespersons = self.env['res.users'].search([('is_salesperson', '=', True)])
        day = datetime.datetime.now().date()
        start_month_date = datetime.datetime(day.year, day.month, 1)

        for sales in salespersons:
            count_leads_per_month = self.search(
                [('user_id', '=', sales.id), ('create_date', '>=', start_month_date),
                 ('create_date', '<=', date_of_warning_month)])
            if len(count_leads_per_month) < leads_per_month:
                mail_template = self.env.ref('crm_leads.mail_template_warning_month_for_leads')
                if mail_template:
                    email_values = {
                        'email_to': (','.join(email_to+[sales.email])),
                        'email_cc': (','.join(email_cc+[sales.email])) or '',
                        'email_from': self.env.user.email,

                    }
                    ctx = {'salesperson_name': sales.name,
                           'month': fields.Date.today().strftime("%B"),
                           'leads_per_month': leads_per_month,
                           'create_leads_per_month': len(count_leads_per_month)}
                    mail_template.with_context(**ctx).send_mail(self.id,
                                                                email_values=email_values,
                                                                force_send=True)

    def get_crm_salesperson_email(self):
        to = []
        cc = []

        send_to = self.env['crm.email'].search([('email_type', '=', 'to')]).mapped('work_email')
        send_cc = self.env['crm.email'].search([('email_type', '=', 'cc')]).mapped('work_email')

        for record in send_to:
            to.append(record)

        for record2 in send_cc:
            cc.append(record2)
        return to, cc
