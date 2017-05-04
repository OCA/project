# -*- coding: utf-8 -*-
# © 2012 - 2013 Daniel Reis
# © 2015 - Antiun Ingeniería S.L. - Sergio Teruel
# © 2017 - Rigoberto Martínez <rigo1985@gmail.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Project Task Materials',
    'summary': 'Record products spent in a Task',
    'version': '10.0.1.0.0',
    'category': "Project Management",
    'author': "Daniel Reis, Tecnativa, Odoo Community Association (OCA)",
    'website': 'https://www.tecnativa.com',
    'license': 'AGPL-3',
    'depends': ['project', 'product'],
    'data': [
        'views/project_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
