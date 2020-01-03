# -*- coding: utf-8 -*-
# Copyright 2019 Kmee Informática LTDA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Project Wsjf',
    'summary': """
        This module implements the Weighted Shortest Job First prioritization model.
    """,
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Kmee Informática LTDA,Odoo Community Association (OCA)',
    'website': 'www.kmee.com.br',
    'depends': [
        'project',
    ],
    'data': [
        'views/project_project.xml',
        'views/project_task.xml',
        'data/project_wsjf_data.xml'
    ],
    'demo': [
    ],
}
