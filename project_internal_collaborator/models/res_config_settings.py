# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    collaborators_task_assigned = fields.Boolean(
        config_parameter="project_collaborator.collaborators_task_assigned"
    )
    collaborators_activity_assigned = fields.Boolean(
        config_parameter="project_collaborator.collaborators_activity_assigned"
    )
