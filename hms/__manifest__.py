{
    'name': 'Hospital Management System',
    'version': '1.0',
    'summary': 'Manage hospital departments, doctors, and patients',
    'license': 'LGPL-3',
    'description': """
        Hospital Management System
        ========================
        Manage departments, doctors, and patients
    """,
    'author': 'Mahmoud Nasr',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/patient_views.xml',
        'views/department_views.xml',
        'views/doctor_views.xml',
    ],
    'installable': True,
    'application': True,
}