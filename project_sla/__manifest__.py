# -*- coding: utf-8 -*-
# © 2013 Daniel Reis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Service Level Agreements',
    'summary': 'Define SLAs for your Contracts',
    'version': '10.0.1.0.0',
    "category": "Project Management",
    'author': "Daniel Reis,Odoo Community Association (OCA)",
    'website': 'https://odoo-community.org/',
    'license': 'AGPL-3',
    'depends': [
        'portal',
        'project_issue',
        ],
    'data': [
        'views/project_sla_view.xml',
        'views/project_sla_control_view.xml',
        'project_sla_control_data.xml',
        'views/analytic_account_view.xml',
        'views/project_view.xml',
        'views/project_issue_view.xml',
        'views/project_task_view.xml',
        'security/ir.model.access.csv',
        'report/report_sla_view.xml',
    ],
    'demo': [
        'project_sla_demo.xml',
        ],
    'installable': True,
}
