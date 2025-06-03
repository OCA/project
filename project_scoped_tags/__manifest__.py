{
    "name": "Project Scoped Tags",
    "version": "16.0.1.0.0",
    "website": "https://github.com/OCA/project",
    "author": "OpenStudio SAS, Odoo Community Association (OCA)",
    "depends": ["project"],
    "data": [
        "views/project_tag_views.xml",
        "views/project_project_views.xml",
        "views/project_task_views.xml",
    ],
    "license": "LGPL-3",
    "application": False,
    "auto_install": False,
    "installable": True,
    "post_init_hook": "post_init_set_scoped_tags",
}
