# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Project Parent',
    'summary': """
        Project Patent.""",
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Odoo Community Association (OCA)',
    'website': 'https://www.github.com/OCA/account-analytic.git',
    'depends': [
        'account_analytic_parent',
        'project',
    ],
    'data': [
        'views/project_parent.xml',
    ]
}
