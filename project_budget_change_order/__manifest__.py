# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': "Project Budget Change Order",
    'summary': "Adds change orders to projects.",
    'author': "Patrick Wilson,Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/project',
    'category': 'Project Management',
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'project',
        'project_budget',
    ],
    'data': [
        'data/change_order_stage.xml',
        'security/project_security.xml',
        'security/ir.model.access.csv',
        'views/project.xml',
        'views/change_order.xml',
        'views/change_order_stage.xml',
        'views/change_order_line.xml',
    ],
    'application': False,
    'development_status': 'Beta',
    'maintainers': ['patrickrwilson'],
}
