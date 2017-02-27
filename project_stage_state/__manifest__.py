# -*- coding: utf-8 -*-
# Daniel Reis, 2014
# GNU Affero General Public License <http://www.gnu.org/licenses/>

{
    'name': 'Add State field to Project Stages',
    'version': '10.0.1.0.0',
    'category': 'Project Management',
    'summary': 'Restore State attribute removed from Project Stages in 8.0',
    'author': "Daniel Reis,Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/project-service',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'project',
    ],
    'data': [
        'views/project_view.xml',
        'security/ir.model.access.csv',
        ],
}
