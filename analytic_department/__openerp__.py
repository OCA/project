# -*- coding: utf-8 -*-
{
    "name": "Analytic Department Categorization",
    "version": "8.0.1.0.0",
    "author": "Camptocamp, Daniel Reis,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Generic Modules/Projects & Services",
    "description": """\
Add Department to Analytic Account and Analytical Line models, and to
corresponding tree, search and form views.
""",
    "website": "http://camptocamp.com",
    "depends": [
        "analytic_base_department",
        "account",
        "hr"],
    "data": ["analytic_view.xml"],
    "installable": True,
}
