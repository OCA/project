# Copyright (C) 2023 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    def _default_project_task_fields_domain(self):
        fields = self.env["project.task"].SELF_READABLE_FIELDS
        return [
            ("model", "=", "project.task"),
            ("name", "in", list(fields)),
        ]

    bypass_restriction = fields.Boolean(
        config_parameter="project_task_restrict_field_update.bypass_restriction"
    )

    restricted_field_ids = fields.Many2many(
        comodel_name="ir.model.fields",
        domain=lambda self: self._default_project_task_fields_domain(),
    )

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        ICPSudo = self.env["ir.config_parameter"].sudo()
        ICPSudo.set_param(
            "project_task_restrict_field_update.restricted_field_ids",
            ",".join(str(i) for i in self.restricted_field_ids.ids),
        )
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env["ir.config_parameter"].sudo()

        # Get Many2many from config
        restricted_field_ids = ICPSudo.get_param(
            "project_task_restrict_field_update.restricted_field_ids", default=False
        )
        if restricted_field_ids:
            res.update(
                restricted_field_ids=[int(r) for r in restricted_field_ids.split(",")]
            )

        return res
