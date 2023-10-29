# Copyright Cetmix OU 2023
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    pr_state_default = fields.Selection(
        selection=lambda self: self.env["project.task"].selection_pr_state(),
        string="Default PR State",
        config_parameter="project_task_pull_request_state.pr_state_default",
        help="Default PR state that will be set when "
        "PR URI is added to a task in this project",
    )
