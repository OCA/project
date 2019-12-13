# © 2017-2019 Elico Corp (https://www.elico-corp.com).
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Project Parent',
    'version': '12.0.3.0.0',
    'license': 'LGPL-3',
    'category': 'project',
    'author': 'Therp B.V., Elico Corp, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/project',
    'depends': [
        'project',
    ],
    'data': [
        'views/project_parent.xml',
    ],
    'post_init_hook': 'restore_parents',
    'installable': True,
}
