# -*- coding: utf-8 -*-
# © 2011 Joël Grand-Guillaume (Camptocamp)
# © 2013 Daniel Reis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Analytic Department Categorization",
    "version": "9.0.1.0.0",
    "author": "Camptocamp, Daniel Reis,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Generic Modules/Projects & Services",
    "description": """\
Add Department to Analytic Account.
No required dependency on Accounting modules.
""",
    "website": "http://camptocamp.com",
    "depends": ["analytic", "hr"],
    "data": ["views/analytic.xml"],
    'test': ['test/analytic.yml'],
    'installable': True,
}
