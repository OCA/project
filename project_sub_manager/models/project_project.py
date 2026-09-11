# Copyright 2026 INVITU (<https://www.invitu.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    sub_manager_ids = fields.Many2many(
        comodel_name="res.users",
        relation="project_project_sub_manager_rel",
        column1="project_id",
        column2="user_id",
        string="Sub Managers",
        domain="[('id', '!=', user_id), ('share', '=', False), ('active', '=', True)]",
    )

    def _message_auto_subscribe_followers(self, updated_values, default_subtype_ids):
        res = super()._message_auto_subscribe_followers(
            updated_values, default_subtype_ids
        )
        if "sub_manager_ids" not in updated_values:
            return res
        sub_manager_ids = self._fields["sub_manager_ids"].convert_to_cache(
            updated_values["sub_manager_ids"],
            self.env["project.project"],
            validate=False,
        )
        for user in self.env["res.users"].browse(sub_manager_ids):
            res.append((user.partner_id.id, default_subtype_ids, False))
        return res
