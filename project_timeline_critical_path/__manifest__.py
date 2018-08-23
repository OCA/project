# Copyright 2018 Onestein
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': "Project Timeline Critical Path",
    'summary': 'Highlight the critical paths of your projects.',
    'author': 'Onestein,Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'website': 'https://github.com/OCA/project',
    'category': 'Project Management',
    'version': '11.0.1.0.0',
    'depends': [
        'project',
        'project_timeline_task_dependency'
    ],
    'external_dependencies': {
        'python': [
            'criticalpath'
        ]
    },
    'data': [
        'templates/assets.xml',
        'views/res_config_settings_view.xml'
    ],
    'installable': True,
}
