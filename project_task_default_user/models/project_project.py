# Copyright 2025 NICO SOLUTIONS - ENGINEERING & IT
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    default_user_ids = fields.Many2many(
        "res.users",
        string="Default Users for Tasks",
        domain=lambda self: [
            (
                "all_group_ids",
                "in",
                self.env.ref("project.group_project_user").id,
            )
        ],
        help="If set, tasks will automatically be assigned to these users. "
        "On new tasks, this applies if no users are set. On stage change, "
        "the users are replaced only if the new stage has default users.",
    )
    project_task_assignment_mode = fields.Selection(
        [
            ("replace", "Replace"),
            ("merge", "Merge"),
        ],
        default="replace",
        help=(
            "Defines how default users are applied:\n"
            "- Replace: overwrite existing users\n"
            "- Merge: add default users to existing ones\n"
            "\n"
            "Applied on task creation and stage changes."
        ),
    )
