# Copyright 2015 Incaser Informatica S.L. - Sergio Teruel
# Copyright 2015 Incaser Informatica S.L. - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import Command, api, fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    def _get_default_type_common(self):
        task_types = self.env["project.task.type"].search([("case_default", "=", True)])
        return task_types

    type_ids = fields.Many2many(default=lambda self: self._get_default_type_common())

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        # The project creation actions of the Project app pass
        # ``default_type_ids: []`` so that projects start without stages,
        # which would bypass the default stages defined in this module.
        if "type_ids" in fields and self.env.context.get("default_type_ids") == []:
            res["type_ids"] = [Command.set(self._get_default_type_common().ids)]
        return res
