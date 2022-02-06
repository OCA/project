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
        if self._context.get("default_project_id"):
            default_project = self.env["project.project"].browse(
                self.env.context["default_project_id"]
            )
        else:
            default_project = self.project_id or self.project_id.subtask_project_id
        ctx = dict(self.env.context)
        ctx = {k: v for k, v in ctx.items() if not k.startswith("search_default_")}
        ctx.update(
            {
                "default_name": self.env.context.get("name", self.name) + ": ",
                "default_parent_id": self.id,
                "default_company_id": default_project.company_id.id
                if default_project
                else self.env.company.id,
            }
        )
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

        action["context"] = ctx

        return action
