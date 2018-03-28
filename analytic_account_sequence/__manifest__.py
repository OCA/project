# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Luxim d.o.o.
# Copyright 2017 Matmoz d.o.o.
# Copyright 2017 Deneroteam.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
<<<<<<< 08efe8674459ca4749597c16797725064524a961
    "name": "Analytic account code sequence",
    "version": "1.0",
    "author": "Eficent",
    "website": "www.eficent.com",
    "category": "Generic Modules/Projects & Services",
    "depends": ["base", "project", "analytic", "project_wbs"],
    "description": """
    """,
    "data": [
        "analytic_account_sequence_view.xml",
        "analytic_account_sequence_data.xml",
        "account_analytic_account_view.xml",
        "security/ir.model.access.csv",
=======
    'name': 'Analytic account code sequence',
    'summary': 'Analytic account code sequence',
    'version': '10.0.1.0.0',
    'author':   'Eficent, '
                'SerpentCS ,'
                'Project Expert Team ,'
                'Odoo Community Association (OCA)',
    'website': 'https://www.github.com/OCA/project',
    'category': 'Project Management',
    'depends': ['project_wbs', 'stock_analytic_account'],
    'data': [
        'views/analytic_account_sequence_view.xml',
        'data/analytic_account_sequence_data.xml',
        'views/account_analytic_account_view.xml',
        'security/ir.model.access.csv',
>>>>>>> Enhance the module descriptions
    ],
    'installable': True,
    'license': 'AGPL-3',
}
