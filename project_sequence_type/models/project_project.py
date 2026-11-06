# Copyright 2026 Ledo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    @api.model_create_multi
    def create(self, vals_list):
        """Use the project type's own sequence when it defines one.

        ``project_sequence`` fills ``sequence_code`` from the global
        ``project.sequence`` when the key is absent. We pre-fill it from the
        type's sequence so that branch is skipped; types without a sequence
        (or projects without a type) keep falling back to the default.
        """
        for vals in vals_list:
            if "sequence_code" in vals or not vals.get("type_id"):
                continue
            sequence = self.env["project.type"].browse(vals["type_id"]).sequence_id
            if sequence:
                vals["sequence_code"] = sequence.next_by_id()
        return super().create(vals_list)
