# Copyright 2026 INVITU (<https://www.invitu.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class ProjectTask(models.Model):
    _inherit = "project.task"

    manual_progress = fields.Float(
        "Manual Progress (%)",
        help="Manually enter the estimated progress of the task",
    )

    @api.constrains("manual_progress")
    def check_progress(self):
        for task in self:
            if task.manual_progress > 100 or task.manual_progress < 0:
                raise ValidationError(
                    _("The manual progress must be between 0 and 100")
                )
