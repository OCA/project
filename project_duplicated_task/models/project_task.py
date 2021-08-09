# Copyright 2021 Akretion (https://www.akretion.com).
# @author Kévin ROche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProjectTask(models.Model):
    _inherit = "project.task"

    task_duplicated_open_ids = fields.Many2many(
        comodel_name="project.task",
        relation="duplicated_open_rel",
        column1="duplicated_open_id",
        column2="task_duplicated_id",
        string="Duplicate Open Task",
        store=True,
        ondelete="restrict",
    )

    task_duplicated_closed_ids = fields.Many2many(
        comodel_name="project.task",
        relation="duplicated_closed_rel",
        column1="duplicated_closed_id",
        column2="task_duplicated_id",
        string="Duplicate Closed Task",
        readonly=True,
        store=True,
        ondelete="restrict",
    )

    task_duplicated_id = fields.Many2one(comodel_name="project.task", string="Task")

    is_duplicate = fields.Boolean(default=False)
    have_duplicate = fields.Boolean(default=False)

    def duplicated_task_status_action(self):
        if not self.is_duplicate:
            self._close_duplicated_task()
            if len(self._get_all_subtasks()) > 0:
                for rec in self._get_all_subtasks():
                    rec._close_duplicated_task()
        else:
            self._reopen_duplicated_task()
            if len(self._get_all_subtasks()) > 0:
                for rec in self._get_all_subtasks():
                    rec._reopen_duplicated_task()

    def _close_duplicated_task(self):
        self.is_duplicate = True
        duplicated_stage = self.env.ref(
            "project_duplicated_task.project_stage_duplicated"
        )
        if duplicated_stage.id not in self.project_id.type_ids.ids:
            self.project_id.type_ids = [(4, duplicated_stage.id)]
        self.stage_id = self.stage_find(
            self.project_id.id, domain=[("id", "=", duplicated_stage.id)]
        )

    def _reopen_duplicated_task(self):
        self.is_duplicate = False
        self.stage_id = self.stage_find(
            self.project_id.id, domain=[("fold", "=", False), ("is_closed", "=", False)]
        )
        self.task_duplicated_open_ids = [
            (3, task.id) for task in self.task_duplicated_open_ids
        ]
        self.task_duplicated_closed_ids = [
            (3, task.id) for task in self.task_duplicated_closed_ids
        ]

    @api.onchange("task_duplicated_open_ids", "parent_id.is_duplicate")
    def _fill_open_duplicated_task(self):
        if self.parent_id.is_duplicate:
            self.is_duplicate = True
            self.task_duplicated_open_ids = [
                (4, task.id) for task in self.parent_id.task_duplicated_open_ids
            ]
        ids_to_close = self.browse(self.task_duplicated_open_ids.ids)
        ids_to_close.have_duplicate = True
        for rec in ids_to_close:
            rec.task_duplicated_closed_ids = [(4, self._origin.id)]
            rec.task_duplicated_closed_ids = [
                (4, task.id) for task in self.task_duplicated_closed_ids
            ]
        # Update the task_duplicated_open_ids of the linked duplicated tasks
        ids_to_update = self.browse(self.task_duplicated_closed_ids.ids)
        for rec in ids_to_update:
            rec.task_duplicated_open_ids = [(6, 0, self.task_duplicated_open_ids.ids)]

    # def write(self, vals):
    #     res = super().write(vals)
    #     for rec in self:
    #         if rec.is_duplicate and len(rec.task_duplicated_open_ids) == 0:
    #             raise ValidationError(
    #                 _(
    #                     "A 'Duplicate Open Task' is required "
    #                     "in order to close this one."
    #                 )
    #             )
    #     return res

    # @api.constrains("is_duplicate", "task_duplicated_open_ids")
    # def _check_task_duplicated_open_presence(self):
    #     for rec in self:
    #         if rec.is_duplicate and len(rec.task_duplicated_open_ids) == 0:
    #             raise ValidationError(
    #                 _(
    #                     "A 'Duplicate Open Task' is required "
    #                     "in order to close this one."
    #                 )
    #             )
