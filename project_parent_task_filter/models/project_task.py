from odoo import api, models


class TaskSub(models.Model):
    _inherit = "project.task"

    @api.model_create_multi
    def create(self, vals_list):
        res = super(TaskSub, self).create(vals_list)
        for vals in vals_list:
            if vals.get("parent_id", False):
                res["display_project_id"] = (
                    self.env["project.task"].browse(vals.get("parent_id")).project_id.id
                )
        return res

    def action_subtask(self):
        action = {
            "type": "ir.actions.act_window",
            "name": "Subtasks of " + self.name,
            "res_model": "project.task",
            "view_mode": "kanban,tree,form,calendar,pivot,graph,activity",
            "search_view_id": [
                self.env.ref("project.view_task_search_form").id,
                "search",
            ],
            "domain": [("id", "!=", self.id), ("id", "child_of", self.id)],
        }
        return action
