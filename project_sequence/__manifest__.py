# Copyright 2023 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

{
    "name": "Project Sequence",
    "summary": "Add a sequence field to projects, filled automatically",
    "version": "17.0.1.0.0",
    "development_status": "Alpha",
    "category": "Services/Project",
    "website": "https://github.com/OCA/project",
    "author": "Moduon, Odoo Community Association (OCA)",
    "maintainers": ["yajo", "anddago78"],
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": ["project"],
    "data": [
        "data/ir_sequence.xml",
        "views/project_project.xml",
        "wizards/res_config_settings_view.xml",
    ],
}
