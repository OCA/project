# -*- coding: utf-8 -*-
{
    'name': 'Business Requirement - Project',
    'category': 'Business Requirements Management',
    'summary': 'Business Requirement - Project',
    'version': '8.0.2.0.0',
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
    'license': 'AGPL-3',
    'installable': True,
}
