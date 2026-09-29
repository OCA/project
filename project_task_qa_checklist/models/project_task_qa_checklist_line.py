# Copyright 2026 - Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo import api, fields, models


class ProjectTaskQaChecklistLine(models.Model):
    _name = "project.task.qa.checklist.line"
    _description = "QA Checklist Line"
    _order = "sequence, id"

    task_id = fields.Many2one(
        comodel_name="project.task",
        required=True,
        ondelete="cascade",
        index=True,
    )
    template_id = fields.Many2one(
        comodel_name="project.task.qa.checklist.template",
        string="Criterion Template",
        ondelete="set null",
    )
    sequence = fields.Integer(default=10)
    name = fields.Char(required=True)
    state = fields.Selection(
        selection=[
            ("pending", "Pending"),
            ("passed", "Passed"),
            ("failed", "Failed"),
            ("not_applicable", "Not Applicable"),
        ],
        default="pending",
        required=True,
    )
    notes = fields.Text()
    reviewed_by = fields.Many2one(comodel_name="res.users", readonly=True)
    reviewed_date = fields.Datetime(readonly=True)

    @api.onchange("state")
    def _onchange_state_reviewer(self):
        for line in self:
            if line.state != "pending":
                line.reviewed_by = self.env.user
                line.reviewed_date = fields.Datetime.now()

    def write(self, vals):
        if "state" in vals and vals["state"] != "pending":
            vals.setdefault("reviewed_by", self.env.user.id)
            vals.setdefault("reviewed_date", fields.Datetime.now())
        return super().write(vals)
