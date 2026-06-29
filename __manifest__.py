{
    'name': 'Corporate Transport Management',
    'version': '17.0.1.0.0',
    'summary': 'Corporate Transport & Fleet Management System',
    'description': """
Corporate Transport Management System
=====================================

Features:
- Driver Management
- Route Management
- Vehicle Assignment
- Transport Scheduling
- Fleet Expense Management
- Leave Management
- Reports
    """,

    'author': 'Randika Dilshan Somasirinayaka',
    'website': 'https://github.com/randika987',

    'category': 'Operations',

    'depends': [
        'base',
        'fleet',
        'hr_holidays',
    ],

    'data': [ 
    'security/ir.model.access.csv',

    'data/driver_sequence.xml',
    'data/vehicle_sequence.xml',
    'data/assignment_sequence.xml',
   

    'views/driver_views.xml',
    'views/vehicle_views.xml',
    'views/assignment_views.xml',
    'views/menu.xml',

    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}