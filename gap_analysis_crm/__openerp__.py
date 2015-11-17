# -*- coding: utf-8 -*-
# © <YEAR(2015)>
# <AUTHOR(Elico Corp, contributor: Eric Caudal, Alex Duan, Xie XiaoPeng)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Gap Analysis - CRM',
    'category': 'project',
    'summary': 'Gap Analysis - CRM',
    'version': '8.0.0.0.2',
    'website': 'www.elico-corp.com',
    "author": "<AUTHOR(S)>, Odoo Community Association (OCA)",
    'depends': [
        'gap_analysis',
        'crm',
    ],
    'data': [
        'views/business_view.xml',
        'views/crm_view.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
}
