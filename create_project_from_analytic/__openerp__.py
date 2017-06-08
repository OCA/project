# -*- coding: utf-8 -*-
# (c) 2015 Eficent - Jordi Ballester
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Create Project from Analytic Account',
    'summary': 'Create a Project from an existing Analytic Account.',
    'version': '8.0.1.0.0',
    'category': "Project Management",
    'author': 'Eficent, '
              'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'depends': ['project'],
    'data': [
        'wizards/create_project_from_analytic_wizard_view.xml',
    ],
    'installable': True,
    'auto_install': True,
}
