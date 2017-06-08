# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Business Requirement Deliverable Default',
    'category': 'Business Requirements Management',
    'summary': 'Business Requirement Deliverable Default',
    'version': '8.0.2.0.2',
    'website': 'www.elico-corp.com',
    "author": "Elico Corp, Odoo Community Association (OCA)",
    'depends': [
        'business_requirement_deliverable',
    ],
    'image': [
		'static/img/bus_req_tree.png',
		'static/img/bus_req_default.png',
		'static/img/bus_req_default2.png'
	],
    'data': [
        "views/business_requirement_deliverable_default.xml",
    ],
    'license': 'AGPL-3',
    'installable': True,
}
