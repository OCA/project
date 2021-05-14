# Copyright (C) 2021 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models


class ProjectTask(models.Model):
    _inherit = "project.task"

    def action_duplicate_subtasks(self):
        action = self.env.ref("project.action_view_task")
        result = action.read()[0]
        task_created = self.env["project.task"]
        for task in self:
            new_task = task.copy()
            task_created |= new_task
            if task.child_ids:
                for child in task.child_ids:
                    new_subtask = child.copy()
                    new_subtask.write({"parent_id": new_task.id})
        if len(task_created) == 1:
            res = self.env.ref("project.view_task_form2")
            result["views"] = [(res and res.id or False, "form")]
            result["res_id"] = new_task.id

        else:
            result["domain"] = "[('id', 'in', " + str(task_created.ids) + ")]"
        return result
