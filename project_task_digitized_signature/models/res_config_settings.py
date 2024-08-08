from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    group_project_sign_task = fields.Boolean(
        "Task Signature",
        implied_group="project_task_digitized_signature.group_project_sign_task",
    )
