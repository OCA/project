# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo import api, fields, models


class TimesheetsAnalysisReport(models.Model):
    _inherit = "timesheets.analysis.report"
    ancestor_task_id = fields.Many2one(
        comodel_name="project.task", string="Ancestor Task", readonly=True
    )

    @api.model
    def _select(self):
        return (
            super()._select()
            + """,
            A.ancestor_task_id AS ancestor_task_id
        """
        )
