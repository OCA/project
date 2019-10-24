# -*- coding: utf-8 -*-
# Copyright 2019 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Website Task',
    'summary': """
        Create tasks from website""",
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'KMEE,Odoo Community Association (OCA)',
    'website': 'https://www.kmee.com.br',
    'depends': [
        'website_form',
        'website_partner',
        'project',
        'project_task_add_very_high',
    ],
    'data': [
        'data/website_data.xml',
        'view/website_task_template.xml',
    ],
    'demo': [
    ],
}
