# -*- coding: utf-8 -*-
{
    "name": "Analytic Department Categorization",
    "version": "2.0",
    "author": "Camptocamp, Daniel Reis",
    "license": "AGPL-3",
    "category": "Generic Modules/Projects & Services",
    "description": """\
Add Department to Analytic Account.
No required dependency on Accounting modules.
""",
    "website": "http://camptocamp.com",
    "depends": ["analytic", "hr"],
    "data": ["analytic_view.xml"],
    'test': ['test/analytic.yml'],
    "installable": True,
}
