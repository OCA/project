# -*- coding: utf-8 -*-
{
    'name': 'Project Issue with Department',
    'version': '9.0.1.0.0',
    "category": "Project Management",
    'description': """\
Add Department field to Project Issues.

Selecting a Project for an issue will automatically populate this with the
Project's defined Department.
""",
    'author': "Daniel Reis,Odoo Community Association (OCA)",
    'website': 'https://odoo-community.org',
    'license': 'AGPL-3',
    'depends': [
        'project_issue',
        'project_department',
    ],
    'data': [
        'project_issue_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
}
