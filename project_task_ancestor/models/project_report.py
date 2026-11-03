# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo import api, fields, models
from odoo.tools import SQL


class ReportProjectTaskUser(models.Model):
    _inherit = "report.project.task.user"
    ancestor_id = fields.Many2one(
        comodel_name="project.task", string="Ancestor Task", readonly=True
    )

    @api.model
    def _select(self):
        return SQL("%s, t.ancestor_id AS ancestor_id", super()._select())

    def _group_by(self):
        return SQL("%s, t.ancestor_id", super()._group_by())
