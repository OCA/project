# Copyright 2026 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from datetime import timedelta

from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    def auto_change_task_state_by_stage(self):
        """Auto-change task states based on stage configuration.

        This method is called by a scheduled action (cron) to automatically
        change task states when they have been in a stage for the configured
        number of days.

        Auto-done is processed first, then auto-cancel. If both apply to the
        same task, auto-done takes precedence.
        """
        self._process_auto_stages("done")
        self._process_auto_stages("cancel")

    def _process_auto_stages(self, mode):
        """Process auto states for tasks in a given stage.

        Args:
            mode (str): The mode ['done', 'cancel'] to process auto states for.

        Raises:
            ValueError: If the mode is not valid.
        """
        if mode not in {"done", "cancel"}:
            raise ValueError("Invalid mode to process auto states.")

        today = fields.Datetime.now()
        stages = self.env["project.task.type"].search([(f"auto_{mode}_days", ">", 0)])

        for stage in stages:
            auto_days = getattr(stage, f"auto_{mode}_days", 0)
            threshold_date = today - timedelta(days=auto_days)
            tasks = self.search(
                [
                    ("stage_id", "=", stage.id),
                    ("date_last_stage_update", "<=", threshold_date),
                    ("state", "in", stage._get_auto_x_allowed_states(mode)),
                ]
            )
            new_state = "1_canceled" if mode == "cancel" else "1_done"
            tasks.write({"state": new_state})
            for task in tasks:
                task.message_post(
                    body=self.env._(
                        "Task automatically %(mode)s after %(days)i days "
                        "in stage '%(stage)s'.",
                        mode=mode,
                        days=auto_days,
                        stage=stage.name,
                    ),
                    message_type="notification",
                    subtype_xmlid="mail.mt_note",
                )
