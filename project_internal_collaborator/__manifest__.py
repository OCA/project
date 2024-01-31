# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Project Internal Collaborator",
    "summary": "Access to internal projects without being a follower",
    "author": "Cetmix, Odoo Community Association (OCA)",
    "category": "Generic Modules/Projects & Services",
    "website": "https://github.com/OCA/project",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "depends": [
        "project",
    ],
    "data": [
        "security/rules.xml",
        "views/res_config_settings.xml",
        "views/project.xml",
    ],
}
