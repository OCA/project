# Copyright 2024 Tecnativa - Carlos López
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ReportProjectTaskUser(models.Model):
    _inherit = "report.project.task.user"

    planned_date_start = fields.Datetime(readonly=True)
    planned_date_end = fields.Datetime(readonly=True)

    def _select(self):
        return (
            super()._select()
            + """,
            t.planned_date_start,
            t.planned_date_end"""
        )

    def _group_by(self):
        return (
            super()._group_by()
            + """,
            t.planned_date_start,
            t.planned_date_end
            """
        )
