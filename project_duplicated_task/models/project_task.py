# Copyright 2021 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    duplicated_main_task_ids = fields.Many2many(
        comodel_name="project.task",
        relation="project_task_duplicate_rel",
        column1="main_id",
        column2="duplicated_id",
        string="Duplicate Main Task",
        store=True,
        ondelete="restrict",
    )

    duplicated_task_ids = fields.Many2many(
        comodel_name="project.task",
        relation="project_task_duplicate_rel",
        column1="duplicated_id",
        column2="main_id",
        string="Duplicate Task",
        readonly=True,
        store=True,
        ondelete="restrict",
    )

    is_duplicate = fields.Boolean(compute="_compute_is_duplicate", store=True)
    have_duplicate = fields.Boolean(compute="_compute_have_duplicate", store=True)

    @api.depends("stage_id")
    def _compute_is_duplicate(self):
        duplicated_stage = self.env.ref(
            "project_duplicated_task.project_stage_duplicated", False
        )
        for record in self:
            if record.stage_id == duplicated_stage:
                record.is_duplicate = True
            else:
                record.is_duplicate = False

    @api.depends("duplicated_main_task_ids")
    def _compute_have_duplicate(self):
        for record in self:
            if (
                record in self.browse(self.duplicated_main_task_ids.ids)
                and not record.have_duplicate
            ):
                record.have_duplicate = True
            else:
                record.have_duplicate = False

    def duplicated_task_status_action(self):
        if not self.is_duplicate:
            self._close_duplicated_task()
            if len(self._get_all_subtasks()) > 0:
                for rec in self._get_all_subtasks():
                    rec._close_duplicated_task()
            return {
                "type": "ir.actions.act_window",
                "name": _("Choose the related task(s)"),
                "view_type": "form",
                "view_mode": "form",
                "view_id": self.env.ref(
                    "project_duplicated_task.duplicated_tasks_form"
                ).id,
                "res_model": self._name,
                "res_id": self.id,
                "target": "new",
            }
        else:
            self._reopen_duplicated_task()
            if len(self._get_all_subtasks()) > 0:
                for rec in self._get_all_subtasks():
                    rec._reopen_duplicated_task()

    def _close_duplicated_task(self):
        duplicated_stage = self.env.ref(
            "project_duplicated_task.project_stage_duplicated"
        )
        if duplicated_stage.id not in self.project_id.type_ids.ids:
            self.project_id.type_ids = [(4, duplicated_stage.id)]
        self.stage_id = self.stage_find(
            self.project_id.id, domain=[("id", "=", duplicated_stage.id)]
        )

    def _reopen_duplicated_task(self):
        self.stage_id = self.stage_find(
            self.project_id.id, domain=[("fold", "=", False), ("is_closed", "=", False)]
        )
        self.duplicated_main_task_ids = [
            (3, task.id) for task in self.duplicated_main_task_ids
        ]
        self.duplicated_task_ids = [(3, task.id) for task in self.duplicated_task_ids]

    @api.onchange("duplicated_main_task_ids")
    def _fill_duplicated_in_main_task(self):
        if self.parent_id.is_duplicate:
            self.duplicated_main_task_ids = [
                (4, task.id) for task in self.parent_id.duplicated_main_task_ids
            ]
            self._close_duplicated_task()
        ids_to_close = self.browse(self.duplicated_main_task_ids.ids)

        for rec in ids_to_close:
            rec.duplicated_task_ids = [(4, self._origin.id)]
            rec.duplicated_task_ids = [
                (4, task.id) for task in self.duplicated_task_ids
            ]
        # Update the duplicated_main_task_ids of the linked duplicated tasks
        ids_to_update = self.browse(self.duplicated_task_ids.ids)
        for rec in ids_to_update:
            rec.duplicated_main_task_ids = [(6, 0, self.duplicated_main_task_ids.ids)]
