# -*- coding: utf-8 -*-
# © 2015 Elico Corp, contributor: Eric Caudal, Alex Duan, Xie XiaoPeng
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Business Requirement - CRM',
    'category': 'Business Requirements Management',
    'summary': 'Business Requirement - CRM',
    'version': '8.0.1.0.0',
    'website': 'www.elico-corp.com',
    "author": "Elico Corp, Odoo Community Association (OCA)",
    'depends': [
        'business_requirement',
        'crm',
    ],
    'data': [
        'views/business_view.xml',
        'views/crm_view.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
}
