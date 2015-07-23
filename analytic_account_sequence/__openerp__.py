# -*- coding: utf-8 -*-

{
<<<<<<< 08efe8674459ca4749597c16797725064524a961
    "name": "Analytic account code sequence",
    "version": "1.0",
    "author": "Eficent",
    "website": "www.eficent.com",
    "category": "Generic Modules/Projects & Services",
    "depends": ["base", "project", "analytic", "project_wbs"],
    "description": """
    """,
    "data": [
        "analytic_account_sequence_view.xml",
        "analytic_account_sequence_data.xml",
        "account_analytic_account_view.xml",
        "security/ir.model.access.csv",
=======
    'name': 'Analytic account code sequence',
    'summary': 'Analytic account code sequence',
    'version': '8.0.1.0.0',
    'author':   'Eficent, '
                'Project Expert Team',
    'contributors': [
        'Jordi Ballester <jordi.ballester@eficent.com>',
        'Matjaž Mozetič <m.mozetic@matmoz.si>',
    ],
    'website': 'http://project.expert',
    'category': 'Project Management',
    'depends': ['base', 'project', 'analytic', 'project_wbs'],
    'data': [
        'views/analytic_account_sequence_view.xml',
        'data/analytic_account_sequence_data.xml',
        'views/account_analytic_account_view.xml',
        'security/ir.model.access.csv',
>>>>>>> Enhance the module descriptions
    ],
    'test': [
    ],
    'installable': True,
    'active': False,
    'certificate': '',
    'application': True,
    'license': 'AGPL-3',
}
