# -*- coding: utf-8 -*-
{
    "name": "Analytic Department Categorization",
    "version": "1.0",
    "author": "Camptocamp, Daniel Reis",
    "license": "AGPL-3",
    "category": "Generic Modules/Projects & Services",
    "description": """\
Add Department to Analytic Account.
No required dependency on Accounting modules.
""",
    "website": "http://camptocamp.com",
    "depends": ["analytic", "hr"],
    "data": ["views/analytic_view.xml",
             "views/res_users_view.xml",
             ],
    'test': ['test/analytic.yml'],
    "installable": True,
}
