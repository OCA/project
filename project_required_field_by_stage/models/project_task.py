# Copyright 2024 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import ast
import json as simplejson

from odoo import _, api, models
from odoo.exceptions import UserError


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
                    if attrs:
                        if attrs.get("required"):
                            attrs["required"] = [
                                "|",
                                ("stage_id", "in", stages_with_field.ids),
                            ] + attrs["required"]
                        else:
                            attrs["required"] = [
                                ("stage_id", "in", stages_with_field.ids)
                            ]
                    else:
                        attrs["required"] = [("stage_id", "in", stages_with_field.ids)]
                    node.set("attrs", simplejson.dumps(attrs))
        return arch, view

    @api.model
    def _get_view_cache_key(self, view_id=None, view_type="form", **options):
        """The override of _get_view changing the required fields labels according
        to the stage makes the view cache dependent on the stages with required fields."""
        key = super()._get_view_cache_key(view_id, view_type, **options)
        return key + tuple(
            self.env["project.task.type"]
            .search([("required_field_ids", "!=", False)])
            .mapped("required_field_ids.name")
        )

    @api.constrains("stage_id")
    def _check_stage_id_(self):
        for this in self:
            stages = this.stage_id.filtered(lambda x: x.required_field_ids)
            for stage in stages:
                fields = (
                    this.env["ir.model.fields"]
                    .sudo()
                    .search([("id", "in", stage.required_field_ids.ids)])
                )
                for rec in this.filtered(lambda x: x.stage_id == stage):
                    for field in fields:
                        if hasattr(rec, field.name) and not getattr(rec, field.name):
                            raise UserError(
                                _(
                                    "Field '%(field)s' is mandatory in stage '%(stage)s'."
                                )
                                % (
                                    {
                                        "field": field.display_name.split(" (")[0],
                                        "stage": stage.display_name,
                                    }
                                )
                            )
