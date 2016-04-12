# -*- coding: utf-8 -*-
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Double alias for project",
    "summary": "Define an alias for tasks and another alias for issues",
    "version": "9.0.1.0.0",
    "category": "Project management",
    "website": "https://www.tecnativa.com/",
    "author": "Tecnativa, "
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "project_issue",
    ],
    "data": [
        "views/project_project_view.xml",
    ],
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
}
