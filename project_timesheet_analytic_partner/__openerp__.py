# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingeniería S.L. - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Partner in timesheets from tasks',
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'summary': 'Propagate task partner to timesheet entries',
    'category': 'Project Management',
    'author': 'Antiun Ingeniería S.L., '
              'Serv. Tecnol. Avanzados - Pedro M. Baeza, '
              'Odoo Community Association (OCA)',
    'website': 'http://www.antiun.com',
    'depends': [
        'analytic_partner',
        'project_timesheet',
    ],
    "installable": True,
    "auto_install": True,
}
