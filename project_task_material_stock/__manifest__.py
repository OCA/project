# -*- coding: utf-8 -*-
# Copyright 2015 Antiun Ingeniería S.L. - Sergio Teruel
# Copyright 2015 Antiun Ingeniería S.L. - Carlos Dauden
# Copyright 2016-2017 Tecnativa - Vicent Cubells
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Project Task Material Stock",
    "summary": "Create stock and analytic moves from "
               "record products spent in a Task",
    "version": "10.0.1.0.0",
    "category": "Project Management",
    "website": "https://www.tecnativa.com/",
    "author": "Tecnativa, "
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "stock_account",
        "project_task_material",
    ],
    "data": [
        "views/project_view.xml",
        "views/project_task_view.xml",
    ],
}
