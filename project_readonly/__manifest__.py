# Copyright 2026  Akretion (https://www.akretion.com).
# @author Sébastien Alix <sebastien.alix@akretion.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

{
    "name": "Project Readonly",
    "summary": "Read-only access to Project documents",
    "version": "19.0.1.0.0",
    "category": "Services/Project",
    "website": "https://github.com/OCA/project",
    "author": "Akretion, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "depends": [
        "project",
    ],
    "data": [
        "security/res_groups.xml",
        "security/ir_rule.xml",
        "security/ir.model.access.csv",
        "views/project_menus.xml",
    ],
    "installable": True,
}
