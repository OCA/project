# -*- coding: utf-8 -*-
# © 2015 Elico Corp, contributor: Eric Caudal, Alex Duan, Xie XiaoPeng
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Business Requirement Task Type',
    'category': 'Business Requirements Management',
    'summary': 'Business Requirement Task Type',
    'version': '8.0.1.0.0',
    'website': 'www.elico-corp.com',
    "author": "Elico Corp, Odoo Community Association (OCA)",
    'depends': [
        'business_requirement_price',
        'base',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/business_view.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
}
