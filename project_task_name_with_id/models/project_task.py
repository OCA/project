# Copyright 2023 Quartile Limited
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.osv import expression


class ProjectTask(models.Model):
    _inherit = "project.task"

    @api.depends("name")
    def _compute_display_name(self):
        for task in self:
            parts = [f"[{task.id}]"]
            if hasattr(task, "key") and task.key:
                parts.append(task.key)
            if task.name:
                parts.append(task.name)
            task.display_name = " ".join(parts)

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        args = args or []
        domain = expression.AND(
            [args, ["|", ("name", operator, name), ("id", operator, name)]]
        )
        records = self.search(domain, limit=limit)
        return [(rec.id, rec.display_name or "") for rec in records]
