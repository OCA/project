# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Business Requirement - Project',
    'category': 'Business Requirements Management',
    'summary': 'Business Requirement - Project',
    'version': '8.0.4.0.4',
    'website': 'www.elico-corp.com',
    "author": "Elico Corp, Odoo Community Association (OCA)",
    'depends': [
        'business_requirement_deliverable',
        'project',
    ],
    'data': [
        'views/business_view.xml',
        'wizard/generate_projects_view.xml',
    ],
	'image': [
		'static/img/bus_req_project.png',
		'static/img/bus_req_tree.png'
	],
    'license': 'AGPL-3',
    'installable': True,
}
