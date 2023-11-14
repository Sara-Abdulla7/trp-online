# -*- coding: utf-8 -*-
{
    "name": "Import Time Sheet Line",
    'summary': 'Import Time Sheet Line from xls file',
    'description': """Import Time Sheet Line from xls file """,
    "version":"16.0.0",
    "category": "Time Sheet",
    'author': 'Mohanad abdalla',
    'website': 'http://www.TRP.sa',
    "depends": ['base','kefah_power'],
    "data": [
        'security/ir.model.access.csv',
        'views/stock_picking_view.xml',
        'wizard/time_sheet_import_wizard.xml',
    ],
    'installable': True,
    'application': True,
    'images':['static/description/banner.png'],
}