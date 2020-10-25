# Copyright 2015 ADHOC SA (http://www.adhoc.com.ar)
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Project Types",
    "version": "14.0.1.0.0",
    "category": "Project",
    "author": "ADHOC SA," "Tecnativa, " "Onestein, " "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/project",
    "license": "AGPL-3",
    "depends": ["project"],
    "data": [
        "views/project_type_views.xml",
        "views/project_project_views.xml",
        "views/project_task_views.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
}
