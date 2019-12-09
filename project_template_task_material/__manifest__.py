# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': "Project Template & Task Material",
    'summary': """Adds function to copy material of tasks when creating
                  a project from template""",
    'author': "Wolfgang Pichler, Odoo Community Association (OCA)",
    'website': "https://github.com/OCA/project",
    'category': 'Project Management',
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'project_template',
        'project_task_material',
        ],
    'application': False,
    'auto_install': True,
    'development_status': 'Beta',
    'maintainers': ['wpichler'],
}
