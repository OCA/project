# Copyright 2021 Graeme Gellatly <graeme@o4sb.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProjectTask(models.Model):

    _inherit = "project.task"

    qc_inspections_ids = fields.One2many(
        comodel_name="qc.inspection",
        inverse_name="task_id",
        copy=False,
        string="Inspections",
        help="Inspections related to this task.",
    )
    created_inspections = fields.Integer(
        compute="_compute_count_inspections", string="Created inspections"
    )
    done_inspections = fields.Integer(
        compute="_compute_count_inspections", string="Done inspections"
    )
    passed_inspections = fields.Integer(
        compute="_compute_count_inspections", string="Inspections OK"
    )
    failed_inspections = fields.Integer(
        compute="_compute_count_inspections", string="Inspections failed"
    )

    @api.depends("qc_inspections_ids", "qc_inspections_ids.state")
    def _compute_count_inspections(self):
        data = self.env["qc.inspection"].read_group(
            [("id", "in", self.mapped("qc_inspections_ids").ids)],
            ["task_id", "state"],
            ["task_id", "state"],
            lazy=False,
        )
        task_data = {}
        for d in data:
            task_data.setdefault(d["task_id"][0], {}).setdefault(d["state"], 0)
            task_data[d["task_id"][0]][d["state"]] += d["__count"]
        for task in self:
            count_data = task_data.get(task.id, {})
            task.created_inspections = sum(count_data.values())
            task.passed_inspections = count_data.get("success", 0)
            task.failed_inspections = count_data.get("failed", 0)
            task.done_inspections = task.passed_inspections + task.failed_inspections
