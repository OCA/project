# Copyright 2016-2017 Tecnativa - Pedro M. Baeza
# Copyright 2017 Tecnativa - Carlos Dauden
# Copyright 2021 Open Source Integrators - Daniel Reis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, exceptions, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    date_start = fields.Datetime("Start Date")

    @api.constrains("date_start", "date_end")
    def _check_date_start_before_date_end(self):
        for task in self:
            if task.date_start and task.date_end and task.date_start > task.date_end:
                raise exceptions.ValidationError(_("Start Date is after End Date."))

    def update_date_end(self, stage_id):
        res = super().update_date_end(stage_id)
        res.pop("date_end", None)
        return res
