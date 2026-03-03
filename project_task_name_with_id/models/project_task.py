# Copyright 2023 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.fields import Domain


class ProjectTask(models.Model):
    _inherit = "project.task"

    @api.depends("name")
    def _compute_display_name(self):
        super()._compute_display_name()
        for task in self:
            if not task.id:
                continue
            task.display_name = f"[{task.id}] {task.display_name}"
        return

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        args = args or []
        domain = Domain.AND(
            [args, ["|", ("name", operator, name), ("id", operator, name)]]
        )
        records = self.search(domain, limit=limit)
        return [(rec.id, rec.display_name or "") for rec in records]
