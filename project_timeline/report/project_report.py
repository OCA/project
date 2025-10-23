# Copyright 2024 Tecnativa - Carlos López
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re

from odoo import fields, models


class ReportProjectTaskUser(models.Model):
    _inherit = "report.project.task.user"

    planned_date_start = fields.Datetime(readonly=True)
    planned_date_end = fields.Datetime(readonly=True)

    def _select(self):
        query = super()._select()
        if not re.search(r"\bt\.planned_date_start\b", query):
            query += ", t.planned_date_start"
        if not re.search(r"\bt\.planned_date_end\b", query):
            query += ", t.planned_date_end"
        return query

    def _group_by(self):
        query = super()._group_by()
        if not re.search(r"\bt\.planned_date_start\b", query):
            query += ", t.planned_date_start"
        if not re.search(r"\bt\.planned_date_end\b", query):
            query += ", t.planned_date_end"
        return query
