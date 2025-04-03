# Copyright 2023 Quartile Limited
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.osv import expression


class ProjectTask(models.Model):
    _inherit = "project.task"

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        domain = expression.AND(
            [args or [], ["|", ("name", operator, name), ("id", operator, name)]]
        )
        recs = self.search(domain, limit=limit)
        return recs.name_get()

    def name_get(self):
        result = super().name_get()
        new_result = []
        for task in result:
            rec = self.browse(task[0])
            name = "[{}] {}".format(rec.id, task[1])
            new_result.append((rec.id, name))
        return new_result
