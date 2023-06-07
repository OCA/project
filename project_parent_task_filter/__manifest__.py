# Copyright 2017 C2i Change 2 improve - Eduardo Magdalena <emagdalena@c2i.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Project Parent Task Filter",
    "summary": "Add a filter to show the parent tasks",
    "version": "15.0.1.1.0",
    "category": "Project",
    "website": "https://github.com/OCA/project",
    "author": "C2i Change 2 improve, " "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["project"],
    "data": ["data/res_config_data.xml", "views/project_task.xml"],
    "installable": True,
    "post_init_hook": "_add_task_display_project",
}
