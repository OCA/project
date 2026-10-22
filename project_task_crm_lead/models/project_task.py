# Copyright 2026 INVITU (<https://www.invitu.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    lead_ids = fields.One2many("crm.lead", "task_id", string="Leads/Opportunities")
    lead_count = fields.Integer(compute="_compute_lead_count")

    @api.depends("lead_ids")
    def _compute_lead_count(self):
        for task in self:
            task.lead_count = len(task.lead_ids)

    def action_view_leads(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "crm.lead",
            "view_mode": "kanban,form",
            "domain": [("task_id", "=", self.id)],
            "context": {
                "search_default_task_id": self.id,
                "default_task_id": self.id,
                "default_type": "opportunity",
            },
            "name": _("Leads from project task %s") % self.name,
        }
