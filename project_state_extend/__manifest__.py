# Copyright 2025 - TODAY, Escodoo.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Project State Extend",
    "summary": """
        Extend project status selection widget with custom states""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Escodoo, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/project",
    "depends": [
        "project",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/project_state_extend_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "project_state_extend/static/src/**/*.esm.js",
            "project_state_extend/static/src/scss/**/*.scss",
        ],
    },
    "demo": [
        "demo/project_state_extend_demo.xml",
    ],
    "installable": True,
}
