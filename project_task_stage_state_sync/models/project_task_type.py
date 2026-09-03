# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ProjectTaskType(models.Model):
    _inherit = "project.task.type"

    sync_state_to_stage = fields.Boolean(
        string="Sync State → Stage",
        help="If ticked, setting a task's state to the value configured above "
        "will automatically move that task to this stage.",
    )

    @api.constrains("sync_state_to_stage", "task_state", "project_ids")
    def _check_unique_sync_per_state_per_project(self):
        for stage in self.filtered("sync_state_to_stage"):
            if not stage.task_state:
                continue
            for project in stage.project_ids:
                conflicting = project.type_ids.filtered(
                    lambda s, stage=stage: s.id != stage.id
                    and s.task_state == stage.task_state
                    and s.sync_state_to_stage
                )
                if conflicting:
                    state_label = dict(stage._get_task_states()).get(
                        stage.task_state, stage.task_state
                    )
                    raise ValidationError(
                        self.env._(
                            "Stage '%(conflicting_stage)s' in project '%(project)s' "
                            "is already configured to move tasks here when their state "
                            "is '%(state)s'. Only one stage per project can have "
                            "Sync State → Stage enabled for the same state value.",
                            conflicting_stage=conflicting[0].name,
                            project=project.name,
                            state=state_label,
                        )
                    )
