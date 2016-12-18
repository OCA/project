# -*- coding: utf-8 -*-
# Copyright 2012 - 2013 Daniel Reis
# Copyright 2015 - Antiun Ingeniería S.L. - Sergio Teruel
# Copyright 2016 - Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Project Task Materials",
    "summary": "Record products spent in a Task",
    "version": "9.0.1.0.0",
    "category": "Project Management",
    "author": "Daniel Reis,"
              "Tecnativa,"
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "project_timesheet",
        "product"
    ],
    "data": [
        "views/project_view.xml",
        "security/ir.model.access.csv",
    ],
}
