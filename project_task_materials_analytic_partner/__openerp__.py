# -*- coding: utf-8 -*-
# © 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Partner in task materials',
    'summary': 'Select alternative partner in task materials',
    'version': '8.0.1.0.0',
    'category': 'Project',
    'license': 'AGPL-3',
    'author': "Tecnativa, "
              "Odoo Community Association (OCA)",
    'website': 'http://www.tecnativa.com',
    'depends': [
        'analytic_partner_hr_timesheet_invoice',
        'project_task_materials_stock',
    ],
    'data': [
        'views/project_view.xml',
    ],
    'installable': True,
}
