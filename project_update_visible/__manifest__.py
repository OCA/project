# Copyright 2023 Binhex (https://www.binhex.cloud)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Project Update Visible",
    "summary": """
        Visible project_id in project.update view form.
    """,
    "author": "Binhex, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/project",
    "category": "Project",
    "version": "16.0.1.0.0",
    "installable": True,
    "license": "AGPL-3",
    "depends": ["sale_timesheet"],
    "data": [
        "views/project_update_views.xml",
    ],
}
