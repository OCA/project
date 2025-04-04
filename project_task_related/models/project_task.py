# Copyright 2024 Tecnativa Carolina Fernandez
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    forward_related_task_ids = fields.Many2many(
        "project.task",
        "project_task_relation",
        "task_id",
        "related_task_id",
        string="Self to other task relation",
    )

    # Inverse relation: Task B -> Task A
    reverse_related_task_ids = fields.Many2many(
        "project.task",
        "project_task_relation",
        "related_task_id",
        "task_id",
        string="Other to self task relation",
    )

    # Displayed field: merged bidirectional field
    related_task_ids = fields.Many2many(
        "project.task",
        compute="_compute_related_tasks",
        inverse="_inverse_related_tasks",
        string="Related Tasks",
        domain="[('id', '!=', id)]",
    )

    @api.depends("forward_related_task_ids", "reverse_related_task_ids")
    def _compute_related_tasks(self):
        for task in self:
            task.related_task_ids = task.forward_related_task_ids
            task.related_task_ids += self.env["project.task"].search(
                [("reverse_related_task_ids", "in", [task.id])]
            )

    def _inverse_related_tasks(self):
        for task in self:
            # Clear old relations
            task.forward_related_task_ids = [(6, 0, task.related_task_ids.ids)]
            task.reverse_related_task_ids = [(6, 0, task.related_task_ids.ids)]
