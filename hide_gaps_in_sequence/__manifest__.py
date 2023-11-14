# -*- coding: utf-8 -*-
{
    'name': "Hide Gaps In Sequence",

    'summary': """
    hide gaps sequence
        """,

    'description': """
        Long description of module's purpose
    """,

    'author': "kascco",
    'website': "https://www.kscco.com",
    'category': 'Account',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/account_journal_kanban.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
