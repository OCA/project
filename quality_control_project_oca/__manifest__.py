# Copyright 2021 O4SB Ltd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Quality Control Project Oca",
    "summary": """
        Adds Quality Control to Projects and Tasks""",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "author": "O4SB Ltd,Odoo Community Association (OCA)",
    "website": "https://o4sb.com",
    "depends": ["project", "quality_control_oca"],
    "data": [
        "security/ir.model.access.csv",
        "views/project_task.xml",
        "views/project_project.xml",
        "views/qc_inspection.xml",
    ],
}
