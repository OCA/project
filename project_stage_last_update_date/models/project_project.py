# Copyright 2024 Tecnativa - Carolina Fernandez
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
from datetime import datetime

from odoo import fields, models


class Project(models.Model):
    _inherit = "project.project"

    stage_last_update_date = fields.Datetime(copy=False, readonly=True)

    def write(self, vals):
        if "stage_id" in vals:
            vals["stage_last_update_date"] = datetime.now()
        return super().write(vals)
