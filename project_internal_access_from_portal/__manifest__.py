# Copyright (C) 2025 Cetmix OÜ
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Internal Project Available in Portal",
    "version": "17.0.1.0.1",
    "summary": "Show internal projects in portal",
    "author": "Cetmix, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Project",
    "website": "https://github.com/OCA/project",
    "depends": ["project"],
    "data": [
        "security/portal_project_rules.xml",
    ],
    "demo": ["demo/demo_data.xml"],
    "installable": True,
    "application": False,
}
