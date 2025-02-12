# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models

from .project import TASK_DEFAULT_COPY_CONTEXT_KEY


class ProjectTask(models.Model):
    _inherit = "project.task"

    def update_date_end(self, stage_id):
        # Refuse to overwrite date_end when we are copying a template
        if self.env.context.get(TASK_DEFAULT_COPY_CONTEXT_KEY):
            return {}
        return super().update_date_end(stage_id)
