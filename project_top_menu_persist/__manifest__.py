# Copyright 2026 OBS Solutions B.V.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "Project Top Menu Persist",
    "summary": "Keep the project top menu and its selected buttons across projects",
    "version": "19.0.1.0.0",
    "category": "Project",
    "website": "https://github.com/OCA/project",
    "author": "OBS Solutions B.V., Odoo Community Association (OCA)",
    "maintainers": ["bosd"],
    "license": "LGPL-3",
    "depends": ["project"],
    "assets": {
        "web.assets_backend": [
            "project_top_menu_persist/static/src/js/**/*",
        ],
        "web.assets_unit_tests": [
            "project_top_menu_persist/static/tests/**/*",
        ],
    },
    "installable": True,
}
