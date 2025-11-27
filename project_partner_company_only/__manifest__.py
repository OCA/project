# Copyright 2026 OpenStudio SAS
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "Project partner can be company only",
    "summary": "Restrict project partner to companies only",
    "version": "16.0.1.0.0",
    "category": "Project",
    "website": "https://github.com/OCA/project",
    "author": "OpenStudio SAS, Odoo Community Association (OCA)",
    "maintainers": ["maisim"],
    "license": "LGPL-3",
    "depends": [
        "base_view_inheritance_extension",
        "project",
    ],
    "data": [
        "views/project_project_views.xml",
    ],
    "installable": True,
}
