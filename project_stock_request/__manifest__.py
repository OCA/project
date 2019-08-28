# Copyright (C) 2019 - TODAY, Patrick Wilson
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Project - Stock Request',
    'summary': 'Create stock requests from a projects and project tasks',
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Pavlov Media, Odoo Community Association (OCA)',
    'category': 'Project',
    'website': 'https://github.com/OCA/project',
    'depends': [
        'stock_request',
        'project',
    ],
    'data': [
        'views/project_views.xml',
        'views/project_task_views.xml',
        'views/stock_request_order_views.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
