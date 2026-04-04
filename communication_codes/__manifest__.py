{
    'name': 'Communication Codes Management',
    'version': '18.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Manage communication codes (SIM) for employees',
    'description': """
Communication Codes Management Module
=====================================

Features:
- Employee communication codes management
- Arabic and RTL language support
- Excel import and export
- Change tracking
- Code version management
- Multi-company support
    """,
    'author': 'Whiba Holding',
    'website': 'https://whiba.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'hr',
        'mail',
    ],
    'external_dependencies': {
        'python': [
            'openpyxl',
        ],
    },
    'data': [
        'security/ir.model.access.csv',
        'security/communication_codes_security.xml',
        'data/communication_codes_data.xml',
        'views/communication_codes_views.xml',
        'views/communication_codes_menu.xml',
        'wizard/import_communication_codes_view.xml',
        'wizard/export_communication_codes_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'communication_codes/static/src/lib/chartjs/chart.umd.min.js',
            'communication_codes/static/src/components/dashboard/dashboard.js',
            'communication_codes/static/src/components/dashboard/dashboard.xml',
            'communication_codes/static/src/components/dashboard/dashboard.scss',
        ],
    },
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
