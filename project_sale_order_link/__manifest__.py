# Copyright 2023 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

{
    "name": "Project Sale Order Link",
    "summary": "Sales order linked to project, tasks or employee map",
    "version": "15.0.1.0.1",
    "development_status": "Alpha",
    "category": "Project",
    "website": "https://github.com/OCA/project",
    "author": "Moduon, Odoo Community Association (OCA)",
    "maintainers": ["EmilioPascual"],
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "sale_timesheet",
    ],
    "data": [
        "views/project_views.xml",
    ],
}
