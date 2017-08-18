# -*- coding: utf-8 -*-
# Copyright 2016 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Project Task Delegation",
    "summary": "Project task delegation",
    "version": "9.0.1.0.0",
    "category": "Project Management",
    "website": "http://sodexis.com/",
    "author": "Sodexis, Inc <dev@sodexis.com>,"
              "Odoo Community Association (OCA),"
              "Odoo SA",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "project",
        "project_timesheet",
    ],
    "data": [
        "security/project_security.xml",
        "wizards/project_task_delegate_view.xml",
        "views/project_view.xml",
        "views/res_config_view.xml",
    ],
}
