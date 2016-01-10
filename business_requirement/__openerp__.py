# -*- coding: utf-8 -*-
{
    'name': 'Business Requirement',
    'category': 'Business Requirements Management',
    'summary': 'Business Requirement',
    'version': '8.0.2.0.0',
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
    'license': 'AGPL-3',
    'installable': True,
}
