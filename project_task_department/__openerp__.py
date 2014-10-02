# -*- coding: utf-8 -*-
{
    "name": "Project Task specific Department",
    "version": "1.0",
    "author": "Daniel Reis",
    "license": "AGPL-3",
    "category": "Generic Modules/Projects & Services",
    "description": """\
Task store the Department they correspond to.
By default this is the Project Department.
This module also makes it manually editable.
""",
    "website": "https://github.com/OCA/project-service",
    "depends": [
        "project_department",
    ],
    "data": ["project_view.xml"],
    "installable": True,
}
