# -*- coding: utf-8 -*-
# © <YEAR(2015)>
# <Elico Corp, contributor: Eric Caudal, Alex Duan, Xie XiaoPeng(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Gap Analysis',
    'category': 'project',
    'summary': 'Gap Analysis',
    'version': '8.0.0.0.2',
    'website': 'www.elico-corp.com',
    "author": "<Elico Corp(S)>, Odoo Community Association (OCA)",
    'depends': [
        'base',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/gap_sequnece.xml',
        'views/business_view.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
}
