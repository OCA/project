# Copyright 2023 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class IrModelFields(models.Model):
    _inherit = "ir.model.fields"

    project_portal_access = fields.Boolean(
        string="Shared with Project Portal Users",
        help="Allow Project Portal Users to access this field.\n"
        "This is only applicable to custom fields, and it doesn't automatically add "
        "the field to any portal view.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        if any(vals.get("project_portal_access") for vals in vals_list):
            self.env["project.task"]._get_portal_custom_field_access.clear_cache(self)
        return super().create(vals_list)

    def write(self, vals):
        if "project_portal_access" in vals:
            self.env["project.task"]._get_portal_custom_field_access.clear_cache(self)
        return super().write(vals)
