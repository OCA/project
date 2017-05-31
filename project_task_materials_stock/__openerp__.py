# -*- coding: utf-8 -*-
# Copyright 2015 Antiun Ingeniería S.L. - Sergio Teruel
# Copyright 2015 Antiun Ingeniería S.L. - Carlos Dauden
# Copyright 2016 Tecnativa - Vicent Cubells
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Project Task Materials Stock",
    "summary": "Create stock and analytic moves from "
               "record products spent in a Task",
    "version": "9.0.1.1.0",
    "category": "Project Management",
    "author": "Antiun Ingeniería S.L.,"
              "Tecnativa, "
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "stock_account",
        "project_task_materials",
    ],
    "data": [
        "views/project_view.xml",
    ],
}
