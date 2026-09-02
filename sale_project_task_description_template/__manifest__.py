# Copyright 2025 NICO SOLUTIONS - ENGINEERING & IT
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).
{
    "name": "Sale Project Task Description Template",
    "summary": (
        "Apply task description templates from products to tasks, "
        "with optional sale info"
    ),
    "version": "19.0.1.0.0",
    "category": "Project",
    "website": "https://github.com/OCA/project",
    "author": "NICO SOLUTIONS - ENGINEERING & IT, Odoo Community Association (OCA)",
    "maintainers": ["NICO-SOLUTIONS"],
    "license": "LGPL-3",
    "depends": ["project_task_description_template", "sale_timesheet"],
    "data": [
        "views/product_template_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
