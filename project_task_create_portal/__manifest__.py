{
    "name": "Project Portal Own Task Management",
    "version": "16.0.1.0.0",
    "summary": "Allow portal users to create and edit their own tasks"
    "from the portal only in a project's pre-configured task stage.",
    "author": "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/project",
    "license": "AGPL-3",
    "category": "Project",
    "depends": [
        "web_editor",
        "project",
        "portal",
    ],
    "data": [
        "views/portal_template.xml",
        "views/project_project_views.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "project_task_create_portal/static/src/js/portal.js",
        ],
        "web_editor.assets_wysiwyg": {
            "project_task_create_portal/static/src/xml/portal_wysiwyg.xml",
        },
    },
    "installable": True,
}
