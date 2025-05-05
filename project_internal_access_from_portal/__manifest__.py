# Copyright (C) 2025 Cetmix OÜ
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Internal Project Available in Portal',
    'version': '16.0.1.0.0',
    'summary': 'Show internal projects in portal',
    'description': """
This module allows portal users to access projects and tasks
marked as "Invited internal users" by enabling a special flag.
    """,
    'category': 'Project',
    'author': 'Your Company / OCA',
    'license': 'AGPL-3',
    'depends': ['project', 'portal'],
    'data': [
        'security/ir.model.access.csv',
        'security/portal_project_rules.xml'
    ],
    'demo': ['demo/demo_data.xml'],
    'installable': True,
    'application': False,
    'auto_install': False,
}