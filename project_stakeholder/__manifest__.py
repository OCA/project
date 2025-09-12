# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Project Stakeholder",
    "version": "18.0.1.0.0",
    "category": "Project",
    "website": "https://github.com/OCA/project",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "summary": "Manage project stakeholders and their roles",
    "depends": [
        "project",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/project_project.xml",
        "views/project_stakeholder_role.xml",
        "views/res_partner.xml",
    ],
}
