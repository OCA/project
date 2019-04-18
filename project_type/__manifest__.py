{
    'name': "Project Type",

    'summary': """
        Project Type""",

    'author': "Patrick Wilson, Odoo Community Association (OCA)",
    'website': "https://github.com/OCA/project",

    'category': 'Project Management',
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['project'],

    # always loaded
    'data': [
        'views/project_type.xml',
        'views/project.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
    ],

    'installable': True,
    'auto_install': False,
    'application': False,
    'development_status': 'Beta',
    'maintainers': ['patrickrwilson'],
}
