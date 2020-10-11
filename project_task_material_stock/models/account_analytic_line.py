# Copyright 2019 Valentin Vinagre <valentin.vinagre@qubiq.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    task_material_id = fields.One2many(
        "project.task.material", "analytic_line_id", string="Project Task Material",
    )

    def _timesheet_postprocess_values(self, values):
        res = super(AccountAnalyticLine, self)._timesheet_postprocess_values(values)
        # Delete the changes in amount if the analytic lines
        # come from task material.
        for key in self.filtered(lambda x: x.task_material_id).ids:
            res[key].pop("amount", None)
        return res
