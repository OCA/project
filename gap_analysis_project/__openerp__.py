# -*- coding: utf-8 -*-
# © <YEAR(2015)>
# <Elico Corp, contributor: Eric Caudal, Alex Duan, Xie XiaoPeng(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Gap Analysis - Project',
    'category': 'project',
    'summary': 'Gap Analysis - Project',
    'version': '8.0.0.0.2',
    'website': 'www.elico-corp.com',
    "author": "Elico Corp(S), Odoo Community Association (OCA)",
    'depends': [
        'gap_analysis',
        'project',
    ],
    'data': [
        'views/business_view.xml',
        'wizard/generate_tasks_view.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
}
