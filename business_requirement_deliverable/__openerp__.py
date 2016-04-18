# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Business Requirement Deliverable',
    'category': 'Business Requirements Management',
    'summary': 'Business Requirement Deliverable',
    'version': '8.0.3.0.3',
    'website': 'www.elico-corp.com',
    "author": "Elico Corp, Odoo Community Association (OCA)",
    'depends': [
        'business_requirement',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/business_view.xml',
        'views/project.xml',
    ],
    'image': [
		'static/img/bus_req.png',
		'static/img/bus_req_deliverable.png',
		'static/img/bus_req_deliverable2.png',
		'static/img/bus_req_resource.png',
		'static/img/bus_req_tree.png'
	],
    'license': 'AGPL-3',
    'installable': True,
}
