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
    'website': 'www.kmee.com.br',
    'depends': [
        'website_form',
        'website_partner',
        'project',
    ],
    'data': [
        'data/website_data.xml',
        'view/website_task_template.xml',
    ],
    'demo': [
    ],
}
