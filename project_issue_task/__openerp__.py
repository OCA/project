# -*- coding: utf-8 -*-
# Copyright 2015 - 2013 Daniel Reis
# Copyright 2016 - Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Project Issue related Tasks',
    'summary': 'Use Tasks to support Issue resolution reports',
    'version': '9.0.1.1.0',
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
