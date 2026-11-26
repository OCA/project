# Copyright 2026 INVITU (<https://www.invitu.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models


class CrmLead(models.Model):
    _inherit = "crm.lead"

    task_id = fields.Many2one("project.task")

    def action_view_task(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "project.task",
            "view_mode": "form",
            "res_id": self.task_id.id,
            "target": "current",
            "name": _("Task: %s") % self.task_id.name,
        }
