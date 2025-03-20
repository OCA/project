import ast
import json

from odoo import _, models


class Project(models.Model):
    _inherit = "project.project"

    def _get_execution(self):
        all_tasks = self.env["project.task"].search(
            [
                ("project_id", "=", self.id),
            ]
        )
        executed_tasks = all_tasks.filtered("stage_id.fold")

        total_planned_hours = sum(all_tasks.mapped("planned_hours"))
        total_excuted_hours = sum(executed_tasks.mapped("planned_hours"))

        if total_excuted_hours and total_planned_hours:
            execution = total_excuted_hours * 100 / total_planned_hours
        else:
            execution = 0

        return {
            "all_task": len(all_tasks),
            "excuted": round(total_excuted_hours),
            "percent": round(execution),
        }

    def _get_dedication(self):
        all_tasks = self.env["project.task"].search(
            [
                ("project_id", "=", self.id),
            ]
        )
        total_planned_hours = sum(all_tasks.mapped("planned_hours"))
        total_dedicated_hours = sum(all_tasks.mapped("effective_hours"))

        if total_dedicated_hours and total_planned_hours:
            dedication = total_dedicated_hours * 100 / total_planned_hours
        else:
            dedication = 0

        return {"dedicated": round(total_dedicated_hours), "percent": round(dedication)}

    def action_view_excuted_tasks(self):
        action = (
            self.env["ir.actions.act_window"]
            .with_context(active_id=self.id)
            ._for_xml_id("project_milestone_status.act_excuted_project_task")
        )
        action["display_name"] = _("%(name)s", name=self.name)
        context = action["context"].replace("active_id", str(self.id))
        context = ast.literal_eval(context)
        context.update({"create": self.active, "active_test": self.active})
        action["context"] = context
        action["domain"] = [("project_id", "=", self.id), ("stage_id.fold", "=", True)]
        return action

    def _get_stat_buttons(self):
        buttons = super()._get_stat_buttons()
        execution = self._get_execution()
        dedication = self._get_dedication()

        if self.task_count and execution["all_task"]:
            percent_tasks = round(self.task_count * 100 / execution["all_task"])
        else:
            percent_tasks = 0

        buttons[0][
            "number"
        ] = f"{self.task_count} / {execution['all_task']} ({percent_tasks}%)"
        buttons.append(
            {
                "icon": "check-circle-o",
                "text": _("Execution"),
                "number": f"{execution['percent']}% ({execution['excuted']}h)",
                "action_type": "object",
                "action": "action_view_excuted_tasks",
                "show": True,
                "sequence": 5,
            }
        )

        buttons.append(
            {
                "icon": "clock-o",
                "text": _("Dedication"),
                "number": f"{dedication['percent']}% ({dedication['dedicated']}h)",
                "action_type": "action",
                "action": "hr_timesheet.act_hr_timesheet_line_by_project",
                "additional_context": json.dumps(
                    {
                        "active_id": self.id,
                    }
                ),
                "show": True,
                "sequence": 6,
            }
        )
        return buttons
