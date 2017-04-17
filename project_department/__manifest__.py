# -*- coding: utf-8 -*-
# Copyright 2014 Joël Grand-Guillaume (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Project Department Categorization",
    "version": "10.0.1.0.0",
    "author": "Camptocamp, Daniel Reis,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Generic Modules/Projects & Services",
    "website": "http://camptocamp.com",
    "depends": [
        "analytic_base_department",
        "project",
    ],
    "data": ["views/project.xml"],
    "auto_install": True,
    'installable': True,
}
