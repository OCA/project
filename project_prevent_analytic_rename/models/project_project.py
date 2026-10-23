# Copyright 2026 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo import models


class ProjectProject(models.Model):
    _inherit = "project.project"

    def write(self, vals):
        if "name" in (vals or {}):
            return super(
                ProjectProject,
                self.with_context(prevent_analytic_rename=True),
            ).write(vals)
        return super().write(vals)
