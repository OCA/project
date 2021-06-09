# Copyright 2021 Graeme Gellatly <graeme@o4sb.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    qc_inspections_ids = fields.One2many(
        comodel_name="qc.inspection",
        inverse_name="project_id",
        copy=False,
        string="Inspections",
        help="Inspections related to this project.",
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
            ["project_id", "state"],
            ["project_id", "state"],
            lazy=False,
        )
        project_data = {}
        for d in data:
            project_data.setdefault(d["project_id"][0], {}).setdefault(d["state"], 0)
            project_data[d["project_id"][0]][d["state"]] += d["__count"]
        for project in self:
            count_data = project_data.get(project.id, {})
            project.created_inspections = sum(count_data.values())
            project.passed_inspections = count_data.get("success", 0)
            project.failed_inspections = count_data.get("failed", 0)
            project.done_inspections = (
                project.passed_inspections + project.failed_inspections
            )
