# Copyright 2024 Tecnativa - Carlos López
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models
from odoo.tools import SQL


class ReportProjectTaskUser(models.Model):
    _inherit = "report.project.task.user"

    planned_date_start = fields.Datetime(readonly=True)
    planned_date_end = fields.Datetime(readonly=True)

    def _select(self):
        return SQL(
            """%s,
            t.planned_date_start,
            t.planned_date_end
            """,
            super()._select(),
        )

    def _group_by(self):
        return SQL(
            """%s,
            t.planned_date_start,
            t.planned_date_end
            """,
            super()._group_by(),
        )
