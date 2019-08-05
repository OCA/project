# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Projects List View',
    'version': '12.0.1.0.0',
    'category': 'Project',
    'website': 'https://github.com/OCA/project',
    'author':
        'Brainbean Apps, '
        'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'summary': 'Projects list view',
    'depends': [
        'project',
    ],
    'data': [
        'views/project_project.xml',
    ],
}
