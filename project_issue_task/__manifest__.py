# -*- coding: utf-8 -*-
# © 2013 Daniel Reis
# © 2017 Rigoberto Martínez <rigo1985@gmail.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Project Issue related Tasks',
    'summary': 'Use Tasks to support Issue resolution reports',
    'version': '10.0.0.1.0',
    'category': 'Project Management',
    'author': "Daniel Reis, Tecnativa, Odoo Community Association (OCA)",
    'website': 'https://www.tecnativa.com',
    'license': 'AGPL-3',
    'depends': [
        'project_issue',
        ],
    'data': [
        'security/ir.model.access.csv',
        'security/project_security.xml',
        'views/project_issue_view.xml',
        'views/project_task_cause_view.xml',
        'views/project_task_view.xml',
        ],
    'installable': True,
}
