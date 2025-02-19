# Copyright (C) 2025 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    use_portal_description = fields.Boolean(
        help="If enabled, portal users will see the portal description"
        " instead of the standard one",
    )
    portal_description = fields.Html(
        sanitize_attributes=False,
        help="Description that will be shown to portal users if "
        "'Use Portal Description' is enabled",
    )
