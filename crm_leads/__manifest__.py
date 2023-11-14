# -*- coding: utf-8 -*-
{
    'name': "Crm Leads",

    'summary': """
    Custom CRM Leads for salesperson
        """,

    'description': """
        Long description of module's purpose
    """,

    'author': "Abdullah/Kascco",
    'company': 'Keffah Alsharq Group ',
    'website': "https://www.kascco.sa",
    'category': 'CRM',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'crm', 'hr'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'security/res_groups.xml',
        'views/res_config_settings.xml',
        'views/res_users.xml',
        'views/crm_email.xml',
        'data/ir_corn_data.xml',
        'data/mail_template_data.xml',
    ],

    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',

}
