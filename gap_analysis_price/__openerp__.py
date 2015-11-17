# -*- coding: utf-8 -*-
# © <YEAR(2015)>
# <AUTHOR(Elico Corp, contributor: Eric Caudal, Alex Duan, Xie XiaoPeng)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Gap Analysis - Financial evaluation',
    'category': 'project',
    'summary': 'Gap Analysis - Financial evaluation',
    'version': '8.0.0.0.2',
    'website': 'www.elico-corp.com',
    "author": "<AUTHOR(S)>, Odoo Community Association (OCA)",
    'depends': [
        'gap_analysis',
    ],
    'data': [
        'views/business_view.xml',
        'security/ir.model.access.csv',
    ],
    'license': 'AGPL-3',
    'installable': True,
}
