# Copyright 2019 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com) - Lois Rilo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Project Wiki',
    'description': 'This module links document pages to projects',
    'version': '11.0.1.0.0',
    "development_status": "Beta",
    'category': 'Project',
    'author': 'Efient, '
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/project',
    'license': 'AGPL-3',
    'depends': [
        'project',
        'document_page',
    ],
    'data': [
        'views/document_page_views.xml',
        'views/project_project_views.xml',
    ],
    'installable': True,
}
