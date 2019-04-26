# Copyright 2018 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Project Teams',
    'summary': 'Create and manage project teams.',
    'author': 'Onestein, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'website': 'https://github.com/OCA/project',
    'category': 'Project Management',
    'version': '11.0.1.0.0',
    'depends': [
        'project',
    ],
    'data': [
        'security/ir_model_access.xml',
        'views/project_project_view.xml',
        'views/project_team_view.xml',
        'views/project_task_view.xml',
        'menuitems.xml'
    ],
}
