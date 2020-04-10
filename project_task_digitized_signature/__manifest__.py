# Copyright 2017 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Project Task Digitized Signature",
    "version": "12.0.1.0.0",
    "author": "Tecnativa, "
               "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/project",
    "category": "Project Management",
    "license": "AGPL-3",
    "depends": [
        "project_task_report",
        "web_widget_digitized_signature",
    ],
    "data": [
        "report/project_task_report.xml",
        "views/project_task_views.xml",
    ],
    "installable": True,
}
