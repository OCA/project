# Copyright 2026 ForgeFlow S.L.
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
{
    "name": "Project Task Customer Reference",
    "summary": (
        "Adds Order Customer Reference to tasks, syncs it to the linked "
        "sale order, and exposes it on website webforms."
    ),
    "version": "19.0.1.0.0",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/project",
    "category": "Project",
    "license": "LGPL-3",
    "depends": ["sale_project", "website_project"],
    "data": [
        "data/website_form.xml",
        "views/project_task_views.xml",
    ],
    "installable": True,
    "application": False,
}
