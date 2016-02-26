# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Business Requirement - CRM',
    'category': 'Business Requirements Management',
    'summary': 'Business Requirement - CRM',
    'version': '8.0.3.0.1',
    'website': 'www.elico-corp.com',
    "author": "Elico Corp, Odoo Community Association (OCA)",
    'depends': [
        'business_requirement_deliverable',
        'crm',
        'sale_crm',
    ],
    'data': [
        'wizard/crm_make_sale_view.xml',
        'views/crm_view.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
}
