# -*- coding: utf-8 -*-
# © 2015
# Elico Corp, contributor: Eric Caudal, Alex Duan, Xie XiaoPeng
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Business Requirement',
    'category': 'Business Requirements Management',
    'summary': 'Business Requirement',
    'version': '8.0.1.0.0',
    'website': 'www.elico-corp.com',
    "author": "<Elico Corp(S)>, Odoo Community Association (OCA)",
    'depends': [
        'base',
        'product',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/business_data.xml',
        'views/business_view.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
}
