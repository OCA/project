from odoo import api, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        res._update_fte_month_lines()
        return res

    def write(self, vals):
        res = super().write(vals)
        self._update_fte_month_lines()
        return res

    def unlink(self):
        for line in self:
            if line.non_billable:
                continue
            fte_line = (
                self.env["project.fte.month.line"]
                .sudo()
                .search(
                    [
                        ("project_id", "=", line.project_id.id),
                        ("month", "=", str(line.date.month)),
                        ("year", "=", line.date.year),
                    ]
                )
            )
            fte_line.executed_hours -= line.unit_amount

        res = super().unlink()
        return res

    def _update_fte_month_lines(self):
        for line in self:
            if not line.project_id or not line.date or line.non_billable:
                continue
            fte_line = (
                self.env["project.fte.month.line"]
                .sudo()
                .search(
                    [
                        ("project_id", "=", line.project_id.id),
                        ("month", "=", str(line.date.month)),
                        ("year", "=", line.date.year),
                    ]
                )
            )
            fte_line._compute_executed_hours()
