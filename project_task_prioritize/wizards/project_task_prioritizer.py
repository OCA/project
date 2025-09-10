# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProjectTaskPrioritizer(models.TransientModel):
    _name = "project.task.prioritizer"
    _description = "Project Task Prioritizer"

    task_ids = fields.Many2many(comodel_name="project.task")
    line_ids = fields.One2many(
        comodel_name="project.task.prioritizer.line", inverse_name="wizard_id"
    )

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        task_ids = self.env.context["active_ids"]
        active_model = self.env.context["active_model"]
        if not task_ids:
            return res
        assert active_model == "project.task", "Bad context propagation"
        tasks = (
            self.env[active_model]
            .browse(task_ids)
            .filtered(lambda t: t.state not in ["cancel", "done"])
        )

        matrix_lines = self._get_matrix_lines(tasks)

        res.update(
            {
                "line_ids": [(0, 0, x) for x in matrix_lines],
                "task_ids": task_ids,
            }
        )
        return res

    def _get_matrix_lines(self, tasks):
        res = []
        for task in tasks:
            for prioritizer_category in task.project_id.prioritizer_category_ids:
                line = task.prioritizer_line_ids.filtered(
                    lambda pcl: pcl.prioritizer_category_id == prioritizer_category  # noqa: B023
                )
                res.append(
                    {
                        "task_id": task.id,
                        "prioritizer_category_id": prioritizer_category.id,
                        "prioritizer_category_line_id": line or False,
                    }
                )
        return res

    def button_validate(self):
        for task in self.task_ids:
            lines = self.line_ids.filtered(lambda ptpl: ptpl.task_id == task)  # noqa: B023
            prioritizer_lines = self.env["prioritizer.category.line"]
            for line in lines:
                prioritizer_lines |= line.prioritizer_category_line_id
            task.prioritizer_line_ids = prioritizer_lines


class ProjectTaskPrioritizerLine(models.TransientModel):
    _name = "project.task.prioritizer.line"
    _description = "Project Task Prioritizer Line"

    wizard_id = fields.Many2one(comodel_name="project.task.prioritizer")
    task_id = fields.Many2one(comodel_name="project.task")
    task_name = fields.Char(related="task_id.name")
    prioritizer_category_id = fields.Many2one(comodel_name="prioritizer.category")
    prioritizer_category_name = fields.Char(related="prioritizer_category_id.name")
    prioritizer_category_line_id = fields.Many2one(
        comodel_name="prioritizer.category.line",
        domain="[('prioritizer_category_id','=',prioritizer_category_id)]",
    )
