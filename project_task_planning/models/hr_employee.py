# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0.en.html).

from odoo import fields, models


class HREmployee(models.Model):
    _inherit = "hr.employee"

    disable_planning = fields.Boolean(
        default=False,
        help="Disable planning and capacity buckets for this employee.",
    )

    bucket_capacity_count = fields.Integer(
        string="Capacity Count",
        compute="_compute_bucket_capacity_count",
    )

    def _compute_bucket_capacity_count(self):
        for employee in self:
            employee.bucket_capacity_count = self.env[
                "hr.employee.bucket"
            ].search_count([("employee_id", "=", employee.id)])

    def action_view_bucket_capacity(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "project_task_planning.action_hr_employee_bucket"
        )
        action["domain"] = [("employee_id", "=", self.id)]
        action["context"] = {
            "default_employee_id": self.id,
            "search_default_employee_id": self.id,
        }
        return action

    def write(self, vals):
        res = super().write(vals)
        if vals.get("disable_planning"):
            self.env["hr.employee.bucket"].search(
                [("employee_id", "in", self.ids)]
            ).unlink()
        return res
