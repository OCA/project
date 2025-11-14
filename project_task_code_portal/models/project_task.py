# Copyright (C) 2025 Cetmix OÜ
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    portal_url = fields.Char(compute="_compute_portal_url")
    portal_url_visible = fields.Boolean(compute="_compute_portal_url")

    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS | {
            "code",
            "portal_url",
            "portal_url_visible",
        }

    @property
    def SELF_WRITABLE_FIELDS(self):
        return super().SELF_WRITABLE_FIELDS | {"code"}

    def _compute_portal_url(self):
        for rec in self:
            rec.portal_url = ""
            rec.portal_url_visible = False
            if rec.project_id.privacy_visibility == "portal":
                rec.portal_url_visible = True
                base_url = rec.get_base_url()
                rec.portal_url = (
                    f"{base_url}/my/projects/{rec.project_id.id}/task/{rec.code}"
                )
