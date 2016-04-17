# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Business Requirement',
    'category': 'Business Requirements Management',
    'summary': 'Business Requirement',
    'version': '8.0.4.0.1',
    'website': 'www.elico-corp.com',
    "author": "Elico Corp, Odoo Community Association (OCA)",
    'depends': [
        'project',
        'product',
    ],
    'data': [
        'data/business_data.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/business_view.xml',
    ],
    'image': [
	'static/description/icon.png',
	'static/img/bus_req.png',
	'static/img/bus_req_alias.png',
	'static/img/bus_req_approved.png',
	'static/img/bus_req_cancel.png',
	'static/img/bus_req_confirmed.png',
	'static/img/bus_req_cust_story.png',
	'static/img/bus_req_done.png',
	'static/img/bus_req_drop.png',
	'static/img/bus_req_tags.png',
	'static/img/bus_req_tags2.png',
	'static/img/bus_req_tree.png'
    ],
    'license': 'AGPL-3',
    'installable': True,
}
