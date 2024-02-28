# Copyright 2023 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.tools import ormcache


class ProjectTask(models.Model):
    _inherit = "project.task"

    @api.model
    @ormcache()
    def _get_portal_custom_field_access(self):
        res = (
            self.env["ir.model.fields"]
            .sudo()
            .search_read(
                [
                    ("model", "=", self._name),
                    ("state", "=", "manual"),
                    ("project_portal_access", "=", True),
                ],
                ["name"],
            )
        )
        return {r["name"] for r in res}

    @property
    def SELF_WRITABLE_FIELDS(self):
        return super().SELF_WRITABLE_FIELDS | self._get_portal_custom_field_access()
