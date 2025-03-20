# Copyright 2024-2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProjectTags(models.Model):
    _inherit = "project.tags"
    _parent_store = True

    parent_id = fields.Many2one(
        comodel_name="project.tags", string="Parent Tag", index=True, ondelete="cascade"
    )
    child_ids = fields.One2many(
        comodel_name="project.tags", inverse_name="parent_id", string="Child Tags"
    )
    parent_path = fields.Char(index=True)

    @api.depends("name", "parent_id")
    def _compute_display_name(self):
        for tag in self:
            names = []
            current = tag
            while current:
                names.append(current.name)
                current = current.parent_id
            tag.display_name = " / ".join(reversed(names))

    @api.constrains("parent_id")
    def _check_parent_id(self):
        if self._has_cycle():
            raise ValidationError(_("You can not create recursive tags."))
