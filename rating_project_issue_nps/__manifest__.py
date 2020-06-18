# Copyright 2020 Commown SCIC SAS (https://commown.fr)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Rating project issue: Net Promoter Score",
    "category": "Project",
    "summary": "Implement net promoter score on top of odoo project issue rating",
    "version": "12.0.1.0.0",
    "author": "Commown SCIC SAS, Akretion, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/project",
    "depends": [
        "project",
    ],
    "data": [
        "data/mail_templates.xml",
        "data/web_templates.xml",
        "views/nps_views.xml",
    ],
    "installable": True,
}
