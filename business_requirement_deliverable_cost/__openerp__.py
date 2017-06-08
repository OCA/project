# -*- coding: utf-8 -*-
# © 2016 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Business Requirement Deliverable Cost Control",
    "summary": "Business Requirement Deliverable Cost Control Module Project",
    "version": "8.0.1.0.1",
    'category': 'Business Requirements Management',
    "website": "www.elico-corp.com",
    "author": "Elico Corp",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "business_requirement_deliverable",
    ],
    'image': [
		'static/img/bus_req_tree.png',
		'static/img/bus_req_acl1.png',
		'static/img/bus_req_acl2.png',
		'static/img/bus_req_acl3.png',
		'static/img/bus_req_control.png'
	],
    "data": [
        "security/business_requirement_deliverable_security.xml",
        "views/business.xml",
    ],
}
