# -*- coding: utf-8 -*-
# © <YEAR(2015)>
# <Elico Corp, contributor: Eric Caudal, Alex Duan, Xie XiaoPeng(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Business Requirement - Project',
    'category': 'Business Requirements Management',
    'summary': 'Business Requirement - Project',
    'version': '8.0.0.1.0',
    'website': 'www.elico-corp.com',
    "author": "Elico Corp(S), Odoo Community Association (OCA)",
    'depends': [
        'business_requirement',
        'project',
    ],
    'data': [
        'views/business_view.xml',
        'wizard/generate_tasks_view.xml',
        'wizard/generate_project_view.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
}
