# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    task_name_display = fields.Selection(
        selection=[
            ("code_name", "Number and Title"),
            ("code", "Number only"),
        ],
        default="code_name",
        required=True,
        help="How the tasks of this project are identified:\n"
        "- Number and Title: the task number followed by its title.\n"
        "- Number only: the task number alone; titles are kept but not "
        "displayed, and are not required.",
    )
