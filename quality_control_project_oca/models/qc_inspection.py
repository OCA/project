# Copyright 2021 Graeme Gellatly <graeme@o4sb.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class QcInspection(models.Model):
    _inherit = "qc.inspection"

    @api.depends("object_id")
    def _compute_project_id(self):
        """Overriden for getting the product from a manufacturing order."""
        for inspection in self:
            if inspection.object_id and inspection.object_id._name == "project.project":
                inspection.project_id = inspection.object_id
            elif inspection.object_id and inspection.object_id._name == "project.task":
                inspection.project_id = inspection.object_id.project_id
                inspection.task_id = inspection.object_id

    def object_selection_values(self):
        objects = super().object_selection_values()
        objects.extend(
            [("project.project", "Project"), ("project.task", "Project Task")]
        )
        return objects

    task_id = fields.Many2one(
        comodel_name="project.task", compute="_compute_project_id", store=True
    )
    project_id = fields.Many2one(
        comodel_name="project.project", compute="_compute_project_id", store=True
    )


class QcInspectionLine(models.Model):
    _inherit = "qc.inspection.line"

    task_id = fields.Many2one(
        comodel_name="project.task",
        related="inspection_id.task_id",
        store=True,
        string="Task",
    )

    project_id = fields.Many2one(
        comodel_name="project.project",
        related="inspection_id.project_id",
        store=True,
        string="Project",
    )
