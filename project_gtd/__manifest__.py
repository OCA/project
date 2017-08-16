# -*- coding: utf-8 -*-
# Copyright 2004-2010 Tiny SPRL <http://tiny.be>.
# Copyright 2017 ABF OSIELL <http://osiell.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Todo Lists',
    'version': '10.0.1.0.0',
    'category': 'Project Management',
    'sequence': 100,
    'summary': 'Personal Tasks, Contexts, Timeboxes',
    'author': "Odoo SA, Odoo Community Association (OCA), ABF OSIELL",
    'license': 'AGPL-3',
    'depends': ['project'],
    'data': [
        'project_gtd_data.xml',
        'project_gtd_view.xml',
        'security/ir.model.access.csv',
        'wizard/project_gtd_empty_view.xml',
        'wizard/project_gtd_fill_view.xml',
    ],
    'demo': ['project_gtd_demo.xml'],
    'installable': True,
    'auto_install': False,
}
