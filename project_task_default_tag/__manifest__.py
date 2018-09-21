# Copyright 2018 PESOL (http://pesol.es)
#                Angel Moya (angel.moya@pesol.es)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    'name': 'Project Task Default Tags',
    'summary': 'Set default tags on project for tasks',
    'version': '11.0.1.0.0',
    'category': 'Project',
    'author': 'PESOL, '
              'Odoo Community Association (OCA)',
    "website": "https://github.com/OCA/project",
    'license': 'AGPL-3',
    'depends': [
        'project',
    ],
    'data': [
        'views/project_view.xml',
    ],
    'installable': True,
}
