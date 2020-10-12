# Copyright 2015 Tecnativa - Sergio Teruel
# Copyright 2015 Tecnativa - Carlos Dauden
# Copyright 2016-2017 Tecnativa - Vicent Cubells
# Copyright 2018 Praxya - Juan Carlos Montoya
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Project Task Material Stock",
    "summary": "Create stock and analytic moves from "
    "record products spent in a Task",
    "version": "13.0.1.0.0",
    "category": "Project Management",
    "website": "https://github.com/OCA/project/",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "depends": ["stock_account", "project_task_material"],
    "data": ["data/data.xml", "views/project_view.xml", "views/project_task_view.xml"],
}
