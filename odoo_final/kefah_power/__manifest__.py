# -*- coding: utf-8 -*-
{
    'name': "Kefah Power",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,
    'author': "TIE",
    'website': "http://www.kascco.com",
    'category': 'Uncategorized',
    'version': '16.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base','base_accounting_kit','analytic','sale','purchase','sale_management','mail','project','hr','ent_hr_employee_updation','product_category_company'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/res_company.xml',
        'views/sale_order.xml',
        'views/purchase.xml',
        'views/product.xml',
        'views/res_partner.xml',
        'wizard/sale_wizerd.xml',
        'wizard/select_products_wizard_view.xml',
        'views/project_custom.xml',
        'views/laborer_custom.xml',
        'views/account.xml',
        'views/hr_transfer_employee.xml',
        'views/old_salary.xml',
        'views/time_sheet.xml',
        'views/import_emp_view.xml',
        'wizard/account_invoice_advanced_payment.xml',
        'wizard/emp_import_wizard.xml',
        'wizard/import_employee_view.xml',
        'data/holiday_data.xml',
    ],
}