# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo import api, fields, models


class ReportProjectTaskUser(models.Model):
    _inherit = "report.project.task.user"
    ancestor_id = fields.Many2one(
        comodel_name="project.task", string="Ancestor Task", readonly=True
    )

    @api.model
    def _select(self):
        return (
            super()._select()
            + """,
            t.ancestor_id as ancestor_id
        """
        )

    def _group_by(self):
        return super()._group_by() + ", t.ancestor_id"
