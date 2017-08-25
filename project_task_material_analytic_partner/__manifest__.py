# -*- coding: utf-8 -*-
# Copyright 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2017 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Partner in task materials',
    'summary': 'Select alternative partner in task materials',
    'version': '10.0.1.0.0',
    'category': 'Project',
    'license': 'AGPL-3',
    'author': "Tecnativa, "
              "Odoo Community Association (OCA)",
    'website': 'https://www.tecnativa.com',
    'depends': [
        'analytic_partner',
        'project_task_material_stock',
    ],
    'data': [
        'views/project_view.xml',
    ],
    'installable': True,
}
