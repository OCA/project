# Copyright 2024 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import ast
import json

from odoo import _, api, models
from odoo.exceptions import UserError
from odoo.osv.expression import OR


def _is_empty(field, value):
    if field.ttype in ("integer", "float", "monetary"):
        # Only False means unset; 0 and 0.0 are valid values
        is_empty = value is False
    elif field.ttype in ("many2one",):
        # Relational: empty recordset or False
        is_empty = not value
    elif field.ttype in ("one2many", "many2many"):
        # Multi-relational: empty recordset
        is_empty = len(value) == 0
    elif field.ttype in ("boolean",):
        # a boolean is  "unset" when it's False.
        # it seems like the only correct interpretation. a boolean will
        # always be true or false. therefore will always have a value.
        is_empty = not value
    else:
        is_empty = value is False or value == ""
    return is_empty


class ProjectTask(models.Model):

    _inherit = "project.task"

    @api.model
    def _get_view(self, view_id=None, view_type="form", **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        stages = self.env["project.task.type"].search(
            [("required_field_ids", "!=", False)]
        )
        if view.type == "form" and stages:
            for field in stages.mapped("required_field_ids"):
                stages_with_field = stages.filtered(
                    lambda stage, field=field: field in stage.required_field_ids
                )
                for node in arch.xpath("//field[@name='%s']" % field.name):
                    attrs = ast.literal_eval(node.attrib.get("attrs", "{}"))
                    required_domain = attrs.get("required", [])
                    attrs["required"] = OR(
                        [required_domain, [("stage_id", "in", stages_with_field.ids)]]
                    )
                    node.set("attrs", json.dumps(attrs))
        return arch, view

    @api.model
    def _get_view_cache_key(self, view_id=None, view_type="form", **options):
        """The override of _get_view changing the required fields labels according
        to the stage makes the view cache dependent on the stages with required fields."""
        key = super()._get_view_cache_key(view_id, view_type, **options)
        stages = self.env["project.task.type"].search(
            [("required_field_ids", "!=", False)]
        )
        return key + tuple(
            (stage.id, field.name)
            for stage in stages
            for field in stage.required_field_ids
        )

    @api.constrains("stage_id")
    def _check_required_fields_by_stage(self):
        for this in self:
            for field in this.stage_id.required_field_ids:
                if hasattr(this, field.name):
                    if _is_empty(field, getattr(this, field.name)):
                        raise UserError(
                            _("Field '%(field)s' is mandatory in stage '%(stage)s'.")
                            % (
                                {
                                    "field": field.display_name.split(" (")[0],
                                    "stage": this.stage_id.display_name,
                                }
                            )
                        )
