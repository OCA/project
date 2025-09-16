# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    prioritizer_category_ids = fields.Many2many("prioritizer.category")
    prioritizer_formula = fields.Text(
        default=lambda self: (
            "# Python expression to calculate prioritizer_value\n"
            "# Available variables:\n"
            "# - prioritizer_sum: sum of prioritizer line values\n"
            "# - max_value: sum of max values from prioritizer categories\n"
            "# - allocated_hours: hours allocated to the project/task\n"
            "# - today: datetime.datetime.today()\n"
            "# - rec: current record (project/task)\n"
            "\n"
            "# Example:\n"
            "prioritizer_sum / (allocated_hours * (max_value - prioritizer_sum + 1)) "
        ),
        help="Define a Python expression to compute the prioritizer value.",
    )
