{
    'name': "Project Task Date Shift",

    'summary': """
        Project Task Date Shift""",

    'author': "Patrick Wilson, Odoo Community Association (OCA)",
    'website': "https://github.com/OCA/project",

    'category': 'Project Management',
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['project',
                'project_stage_closed'],

    # always loaded
    'data': [
        'views/project.xml',
        'views/project_task.xml'
    ],

    'application': False,
    'development_status': 'Beta',
    'maintainers': ['patrickrwilson'],
}
