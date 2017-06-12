# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Project Timesheet Currency',
    'summary': """Multi-currency analytic costs""",
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Camptocamp,Odoo Community Association (OCA)',
    'website': 'https://www.camptocamp.com',
    'depends': [
        'analytic',
        'sale_timesheet',
        'project',
        'account',
    ],
    'data': [
        'security/record_rules.yml',
        'security/analytic_security.xml',
        'security/project_security.xml',
        'views/analytic.xml',
    ]
}
