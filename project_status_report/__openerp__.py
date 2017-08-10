# -*- coding: utf-8 -*-
# Copyright <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Project Status Report",
    "summary": "Periodically report on the status of projects",
    "version": "8.0.1.0.0",
    "category": "Project",
    "website": "https://github.com/oca/project",
    "author": "Daniel Reis, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "project",
    ],
    "data": [
        #"security/ir.model.access.csv",
        "views/project_project_view.xml",
        "views/project_status_report_view.xml",
    ],
}
