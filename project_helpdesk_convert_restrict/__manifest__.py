# Copyright 2026 Camptocamp SA
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Restrict Task to Ticket Conversion",
    "summary": "Only convert tasks of portal-visible projects into tickets",
    "version": "18.0.1.0.0",
    "category": "Project",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "maintainers": ["divad1196"],
    "license": "AGPL-3",
    "depends": [
        "project_helpdesk",
    ],
    "website": "https://github.com/OCA/project",
    "data": [
        "views/res_config_settings_views.xml",
    ],
    "installable": True,
}
