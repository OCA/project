# -*- coding: utf-8 -*-
{
    'name': 'Project Issue related Tasks',
    'summary': 'Use Tasks to support Issue resolution reports',
    'version': '10.0.1.0.0',
    'category': 'Project Management',
    'author': "Daniel Reis,"
              "Tecnativa, "
              "Odoo Community Association (OCA)",
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
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
}
