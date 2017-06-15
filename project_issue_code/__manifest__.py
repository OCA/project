# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Project Issue Code",
    "version": "10.0.1.0.0",
    "summary": "Adding Field Code For Project Issue",
    "author": "OpenSynergy Indonesia,Odoo Community Association (OCA)",
    "website": "https://opensynergy-indonesia.com",
    "category": "Project Management",
    "depends": [
        "project_issue",
    ],
    "data": [
        "data/project_issue_sequence.xml",
        "views/project_issue_view.xml",
    ],
    "installable": True,
    "license": "AGPL-3",
    "pre_init_hook": "create_code_equal_to_id",
    "post_init_hook": "assign_old_sequences",
}
