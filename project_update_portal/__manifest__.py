# Copyright 2025 Escodoo <https://escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Project Update Portal Access",
    "version": "16.0.1.0.0",
    "summary": "Allows portal access for project and update followers",
    "author": "Escodoo, Odoo Community Association (OCA)",
    "maintainers": ["marcelsavegnago"],
    "license": "AGPL-3",
    "category": "Project",
    "website": "https://github.com/OCA/project",
    "depends": ["project", "portal"],
    "data": [
        "security/ir.model.access.xml",
        "security/portal_project_update_rules.xml",
        "views/portal_project_update_inherit.xml",
        "views/portal_project_update_templates.xml",
    ],
    "installable": True,
    "application": False,
}
