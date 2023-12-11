# Copyright (C) 2021 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    @api.model
    def _extract_action_dict(self, action):
        action = action.sudo()
        return {
            "name": action.name,
            "res_model": action.res_model,
            "view_mode": action.view_mode,
            "context": action.context,
            "domain": action.domain,
            "search_view_id": action.search_view_id,
            "help": action.help,
        }

    def action_duplicate_subtasks(self):
        action = self._extract_action_dict(self.env.ref("project.action_view_task"))
        task_created = self.env["project.task"]
        for task in self:
            new_task = task.copy()
            task_created |= new_task
            if task.child_ids:

                def duplicate_childs(task, new_task):
                    if task.child_ids:
                        for child in task.child_ids:
                            new_subtask = child.copy()
                            new_subtask.write({"parent_id": new_task.id})
                            duplicate_childs(child, new_subtask)

                duplicate_childs(task, new_task)

        if len(task_created) == 1:
            res = self.env.ref("project.view_task_form2")
            action["views"] = [(res and res.id or False, "form")]
            action["res_id"] = new_task.id
            action["context"] = {
                "form_view_initial_mode": "edit",
                "force_detailed_view": "true",
            }

        else:
            action["domain"] = "[('id', 'in', " + str(task_created.ids) + ")]"
        return action
