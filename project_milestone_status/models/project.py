import json

from odoo import models


class Project(models.Model):
    _inherit = "project.project"

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

    def _get_stat_buttons(self):
        buttons = super()._get_stat_buttons()
        execution = self._get_execution()
        dedication = self._get_dedication()

        if execution["executed_task"] and execution["all_task"]:
            percent_tasks = round(
                execution["executed_task"] * 100 / execution["all_task"]
            )
        else:
            percent_tasks = 0

        buttons[0]["number"] = (
            f"{execution['executed_task']} / {execution['all_task']} ({percent_tasks}%)"
        )
        buttons.append(
            {
                "icon": "check-circle-o",
                "text": self.env._("Execution"),
                "number": f"{execution['percent']}% ({execution['executed']}h)",
                "action_type": "object",
                "action": "action_view_executed_tasks",
                "show": True,
                "sequence": 5,
            }
        )

        buttons.append(
            {
                "icon": "clock-o",
                "text": self.env._("Dedication"),
                "number": f"{dedication['percent']}% ({dedication['dedicated']}h)",
                "action_type": "action",
                "action": "hr_timesheet.act_hr_timesheet_line_by_project",
                "additional_context": json.dumps(
                    {
                        "id": self.id,
                    }
                ),
                "show": True,
                "sequence": 6,
            }
        )
        return buttons
