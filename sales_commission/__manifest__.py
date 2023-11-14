# -*- coding: utf-8 -*-
{
    'name': "Sales Commission ",

    'summary': """
    compute Sales Commission per [Quarter, Half year, Year],
        """,

    'description': """
        Long description of module's     purpose
    """,

    'author': "Abdullah/TRP",
    'website': "https://www.kascco.com",

    # for the full list
    'category': 'Sales/TRP',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'sale', 'sale_management', 'account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/sale_commission.xml',
        'views/sale_commission_line.xml',
        'views/sale_order.xml',
        'views/account_move.xml',
        'views/hr_employee.xml',
        'views/res_users.xml',
        'views/ir_cron.xml',
        'data/ir_corn_data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
