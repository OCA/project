
{
    'name': 'Project task Merge Wizard',
    'version': '12.0.1.0.1',
    'category': 'Project Management',
    'author': 'Odoo SA, '
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/project',
    'license': 'AGPL-3',
    'depends': [
        'project',
    ],
    'data': [
        'wizard/project_task_merge_wizard_views.xml',
        'data/project_data.xml',
    ],
    'installable': True,
}
