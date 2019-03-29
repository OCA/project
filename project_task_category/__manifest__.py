# © 2017-2019 Elico Corp (https://www.elico-corp.com).
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Project Task Categories',
    'summary': 'Allow unique category for Tasks',
    'version': '12.0.1.1.0',
    'author': 'Elico Corp, Odoo Community Association (OCA)',
    'license': 'LGPL-3',
    'category': 'Project Management',
    'website': 'https://github.com/OCA/project',
    'depends': [
        'project',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/project_data.xml',
        'views/project_categ_view.xml',
        'views/project_task_view.xml',
    ],
    'installable': True,
}
