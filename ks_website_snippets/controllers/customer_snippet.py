import json
from odoo import http
from odoo.http import request
from odoo.exceptions import UserError


class CustomerSnippet(http.Controller):
    @http.route('/customers/view', type='http', auth='public', website=True)
    def view_customers(self, page=1):
        total_count = request.env['res.partner'].sudo().search_count(
            [('customer_rank', '>', 0)])
        pager = request.website.pager(
            url='/customers/view',
            total=total_count,
            page=page,
            step=12
        )
        customers = request.env['res.partner'].sudo().search([
            ('customer_rank', '>', 0)], limit=12, offset=(int(page) - 1) * 12)
        total = round(total_count / 12)
        return http.request.render('ks_website_snippets.all_customers', {
            'customers': customers,
            'pager': pager,
            'page': int(page),
            'hasPrev': int(page) > 1,
            'hasNext': int(page) <= total,
        })

    @http.route('/vendor/view', type='http', auth='public',
                website=True)
    def view_vendors(self, page=1):
        total_count = request.env['res.partner'].sudo().search_count(
            [('supplier_rank', '>', 0)])
        pager = request.website.pager(
            url='/customers/view',
            total=total_count,
            page=page,
            step=12
        )
        customers = request.env['res.partner'].sudo().search([
            ('supplier_rank', '>', 0)], limit=12, offset=(int(page) - 1) * 12)
        total = round(total_count / 12)
        return http.request.render('ks_website_snippets.all_vendors', {
            'customers': customers,
            'pager': pager,
            'page': int(page),
            'hasPrev': int(page) > 1,
            'hasNext': int(page) <= total,
        })

    @http.route('/customer/hierarchy', type='json', auth='public',
                website=True)
    def get_hierarchy_data(self):
        employees = request.env['hr.employee'].sudo().sudo().search(
            [('parent_id', '=', False)])
        names = []
        if len(employees) == 1:
            result = request.env['hr.organizational.chart'].sudo().get_employee_data(
                employees.id)
            return result
        elif len(employees) == 0:
            return {'Error': "Don't need to set manager to an "
                             "employee at the top of the chart"}
        else:
            for emp in employees:
                names.append(emp.name)
            return {'Error': "These employee have no Manager %s" % names}

    @http.route('/website/snippet/special/render', type='json', auth='public',
                website=True)
    def render_template(self, **kwargs):
        customer = []
        web_customer = []
        new_list = []
        list = []
        for i in request.env['res.partner'].sudo().search([('customer_rank',
                                                            '>', 0)], limit=16):
            customer.append([
                i.id, i.name, i.image_1920,
            ])
        for i in request.env['res.partner'].sudo().search([('is_web_customer',
                                                            '=', True)]):
            web_customer.append([
                i.id, i.name, i.image_1920,
            ])
        for i in range(0, len(customer), 4):
            new_list.append(customer[i:i + 4])
        for i in range(0, len(web_customer), 4):
            list.append(web_customer[i:i + 4])
        if kwargs.get('template') == 'ks_website_snippets.dynamic_c1' or kwargs.get('template') == 'ks_website_snippets.dynamic_s1':
            if not new_list:
                return {
                    'qcontext':  'No Data Found'
                }
            else:
                return {
                    'qcontext': new_list
                }
        else:
            if not list:
                return {
                    'qcontext': 'No Data Found'
                }
            else:
                return {
                    'qcontext': list
                }

    @http.route('/website/snippet/vendor/render', type='json', auth='public',
                website=True)
    def render_vendor_template(self, **kwargs):
        supplier = []
        web_supplier = []
        new_list = []
        list = []
        for i in request.env['res.partner'].sudo().search([('supplier_rank',
                                                            '>', 0)], limit=16):
            supplier.append([
                i.id, i.name, i.image_1920,
            ])
        for i in request.env['res.partner'].sudo().search([('is_supplier',
                                                            '=', True)]):
            web_supplier.append([
                i.id, i.name, i.image_1920,
            ])
        for i in range(0, len(supplier), 4):
            new_list.append(supplier[i:i + 4])
        for i in range(0, len(web_supplier), 4):
            list.append(web_supplier[i:i + 4])
        if kwargs.get('template') == 'ks_website_snippets.supplier_dynamic_c1' or kwargs.get('template') == 'ks_website_snippets.supplier_dynamic_s1':
            if not new_list:
                return {
                    'qcontext': 'No Data Found'
                }
            else:
                return {
                    'qcontext': new_list
                }
        else:
            if not list:
                return {
                    'qcontext': 'No Data Found'
                }
            else:
                return {
                    'qcontext': list
                }

    @http.route('/partner/snippet', type='json', auth='public',
                website=True)
    def render_partner_template(self, **kwargs):
        partner = []
        new_list = []
        for i in request.env['web.partner'].sudo().search([]):
            partner.append([
                i.image_1920, i.name
            ])
        for i in range(0, len(partner), 4):
            new_list.append(partner[i:i + 4])
        if new_list:
            return {
                'qcontext': new_list
            }
        else:
            return {
                'qcontext': 'No Data Found'
            }

    @http.route('/employee/of/the/month', type='json', auth='public',
                website=True)
    def employee_of_the_month(self, **kwargs):
        parameters = request.env['ir.config_parameter'].sudo().search([
            ('key', 'in',
             ['ks_website_snippets.attendance', 'ks_website_snippets.task'])
        ])
        attendance = parameters.filtered(
            lambda p: p.key == 'ks_website_snippets.attendance').value
        task = parameters.filtered(
            lambda p: p.key == 'ks_website_snippets.task').value
        top_employees = []
        if attendance and task:
            top_employees = request.env[
                'hr.employee'].sudo().get_top_10_employees_combined()
        elif attendance:
            top_employees = request.env[
                'hr.employee'].sudo().get_top_10_employees_by_attendance()
        elif task:
            top_employees = request.env[
                'hr.employee'].sudo().get_top_10_employees_by_project_tasks()
        if top_employees:
            result = [{'id': rec.id, 'name': rec.name, 'img': rec.image_1920} for rec in
                      top_employees]
        else:
            employees = request.env['hr.employee'].sudo().search([], limit=10)
            result = [{'id': rec.id, 'name': rec.name, 'img': rec.image_1920} for rec in employees]
        return result
