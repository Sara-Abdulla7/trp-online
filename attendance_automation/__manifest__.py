{
    'name': 'Attendance Automation ',
    'version': '16.0.1.0.0',
    'summary': 'Employee Attendance',
    'description': """
        Helps you to manage Employee Attendance.
        """,
    'category': 'Generic Modules/Human Resources',
    'author': "TRP team deveploer",
    'company': 'TRP',
    'maintainer': 'Technology Resources Planning',
    'website': "https://www.trp.sa",
    'depends': ['base','hr_attendance','oh_hr_zk_attendance'],

    'data': [
        'security/ir.model.access.csv',
        'views/attendance_automation.xml',
        'views/employee_approval.xml',
        'views/attendance_settings.xml',
        'views/default_time.xml',
        'views/attendance_delay_auto.xml',
        'data/send_email.xml',
        'demo/demo_default.xml',

        # 'views/attendance_automation.xml',
        'views/zk_machine_custom.xml',
        # 'data/send_email.xml',
        
    ],
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
