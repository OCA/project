# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
	'name': 'Project Task Materials',
	'summary': 'Record products spent in a Task',
	'version': '10.0.1.0.0',
	'category': "Project Management",
	'author':   "Daniel Reis,"
		        "Antiun Ingeniería S.L.,"
		        "Tecnativa,"
			    "Odoo Community Association (OCA)",
	'license': 'AGPL-3',
	'depends': [
            'project',
            'product',
    ],
	'data': [
		'views/project_view.xml',
		'security/ir.model.access.csv',
	],
	'installable': False,
}
