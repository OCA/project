# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': "Project Budget",
    'summary': "Adds budget management to projects.",
    'author': "Patrick Wilson,Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/project',
    'category': 'Project Management',
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'project',
        'account_budget_oca',
        'hr_timesheet',
    ],
    'data': [
        'security/project_security.xml',
        'security/ir.model.access.csv',
        'views/project.xml',
        'views/account_budget.xml',
    ],
    'application': False,
    'development_status': 'Beta',
    'maintainers': ['patrickrwilson'],
}
