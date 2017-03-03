# -*- coding: utf-8 -*-
# Copyright 2017 Specialty Medical Drugstore
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Project Task Pull Request",
    "summary": "Adds a field for a PR URI to project tasks",
    "version": "10.0.1.0.0",
    "category": "Project Management",
    "website": "https://odoo-community.org/",
    "author": "SMDrugstore, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "project",
        "project_stage_state",
    ],
    "data": [
        "views/project_task_pull_request_view.xml",
    ],
}
