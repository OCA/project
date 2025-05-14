# Copyright 2023 Quartile Limited
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.osv import expression


class ProjectTask(models.Model):
    _inherit = "project.task"

    @api.depends("name")
    def _compute_display_name(self):
        super()._compute_display_name()
        for task in self:
            task.display_name = f"[{task.id}] {task.display_name}"
        return

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        args = args or []
        domain = expression.AND(
            [args, ["|", ("name", operator, name), ("id", operator, name)]]
        )
        records = self.search(domain, limit=limit)
        return [(rec.id, rec.display_name or "") for rec in records]
