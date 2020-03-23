# Copyright 2016-2017 Tecnativa - Pedro M. Baeza
# Copyright 2017 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class ProjectTask(models.Model):
    _inherit = "project.task"

    def update_date_end(self, stage_id):
        res = super().update_date_end(stage_id)
        res.pop("date_end", None)
        return res
