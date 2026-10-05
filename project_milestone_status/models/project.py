from odoo import api, fields, models


class Project(models.Model):
    _inherit = "project.project"

    execution_percent = fields.Integer(compute="_compute_execution_stats")
    execution_hours = fields.Integer(compute="_compute_execution_stats")
    dedication_percent = fields.Integer(compute="_compute_dedication_stats")
    dedication_hours = fields.Integer(compute="_compute_dedication_stats")

    def _get_execution(self):
        all_tasks = self.tasks
        executed_tasks = all_tasks.filtered("stage_id.fold")

        total_allocated_hours = sum(all_tasks.mapped("allocated_hours"))
        total_executed_hours = sum(executed_tasks.mapped("allocated_hours"))

        if total_executed_hours and total_allocated_hours:
            execution = total_executed_hours * 100 / total_allocated_hours
        else:
            execution = 0

        return {
            "all_task": len(all_tasks),
            "executed_task": len(executed_tasks),
            "executed": round(total_executed_hours),
            "percent": round(execution),
        }

    def _get_dedication(self):
        total_allocated_hours = sum(self.tasks.mapped("allocated_hours"))
        total_dedicated_hours = sum(self.tasks.mapped("effective_hours"))

        if total_dedicated_hours and total_allocated_hours:
            dedication = total_dedicated_hours * 100 / total_allocated_hours
        else:
            dedication = 0

        return {"dedicated": round(total_dedicated_hours), "percent": round(dedication)}

    @api.depends("tasks.stage_id.fold", "tasks.allocated_hours")
    def _compute_execution_stats(self):
        for project in self:
            execution = project._get_execution()
            project.execution_percent = execution["percent"]
            project.execution_hours = execution["executed"]

    @api.depends("tasks.allocated_hours", "tasks.effective_hours")
    def _compute_dedication_stats(self):
        for project in self:
            dedication = project._get_dedication()
            project.dedication_percent = dedication["percent"]
            project.dedication_hours = dedication["dedicated"]

    def action_view_executed_tasks(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "project_milestone_status.act_excuted_project_task"
        )
        action.update(
            {
                "name": self.env._("%(name)s", name=self.name),
                "domain": [
                    ("project_id", "=", self.id),
                    ("display_in_project", "=", True),
                    ("stage_id.fold", "=", True),
                ],
                "context": {
                    **self.env.context,
                    "default_project_id": self.id,
                    "show_project_update": True,
                    "create": self.active,
                    "active_test": self.active,
                },
            }
        )
        return action
