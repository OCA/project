# Copyright (C) 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models


class ProjectTask(models.Model):
    _inherit = "project.task"

    def action_duplicate_subtasks(self):
        action = self.env.ref("project.action_view_task")
        result = action.read()[0]
        task_created = self.env["project.task"]
        for task in self:
            # Since 18.0, task.copy() natively duplicates the whole subtask
            # tree, so no manual recursion is needed anymore.
            new_task = task.copy()
            task_created |= new_task

        if len(task_created) == 1:
            res = self.env.ref("project.view_task_form2")
            result["views"] = [(res and res.id or False, "form")]
            result["res_id"] = new_task.id
            action["context"] = {
                "form_view_initial_mode": "edit",
                "force_detailed_view": "true",
            }

        else:
            result["domain"] = "[('id', 'in', " + str(task_created.ids) + ")]"
        return result
