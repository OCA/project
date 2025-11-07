# Copyright 2025 Moduon Team, S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Project Task Ancestor",
    "version": "18.0.1.0.1",
    "category": "Services/Project",
    "website": "https://github.com/OCA/project",
    "author": "Moduon, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "application": False,
    "depends": ["hr_timesheet"],
    "maintainers": ["rafaelbn", "chienandalu", "Andrii9090"],
    "data": [
        "views/hr_timesheet_views.xml",
        "views/project_task_views.xml",
    ],
}
