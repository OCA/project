# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class HrLeave(models.Model):
    _inherit = "hr.leave"

    @api.model_create_multi
    def create(self, vals_list):
        leaves = super().create(vals_list)
        leaves._update_capacity_lines()
        return leaves

    def write(self, values):
        res = super().write(values)
        self._update_capacity_lines()
        return res

    def _update_capacity_lines(self):
        capacity_vals = []
        CapacityLine = self.env["capacity.line"].sudo()
        # XXX try to be smarter and only unlink those needing unlinking, update the others
        CapacityLine.search(
            [("res_id", "in", self.ids), ("res_model", "=", self._name)]
        ).unlink()
        leaves = self.filtered_domain([("state", "!=", "refuse")])
        for leave in leaves:
            if not leave.employee_id.main_role_id:
                _logger.warning(
                    "No capacity role for employee %s (%s)",
                    leave.employee_id.name,
                    leave.employee_id,
                )
                continue
            if leave.state == "validate":
                # will be handled by the resource.calendar.leaves
                continue
            else:
                capacity_type = "forecast"
            capacity_vals += CapacityLine.prepare_capacity_lines(
                name=_("Leave"),
                date_from=leave.date_from.date(),
                date_to=leave.date_to.date(),
                capacity_type=capacity_type,
                capacity_hours=CapacityLine.convert_days_to_hours(
                    -1 * leave.number_of_days
                ),
                unit_cost=leave.employee_id.timesheet_cost,
                capacity_role_id=leave.employee_id.main_role_id.id,
                hr_leave_id=leave.id,
                res_model=self._name,
                res_id=leave.id,
            )
        return CapacityLine.create(capacity_vals)

    @api.model
    def _recompute_capacity_lines(self, force_company_id=None):
        today = fields.Date.context_today(self)
        if force_company_id:
            companies = self.env["res.company"].browse(force_company_id)
        else:
            companies = self.env["res.company"].search([])
        for company in companies:
            to_update = self.with_company(company).search(
                [
                    ("date_to", ">=", today),
                    ("employee_company_id", "=", company.id),
                ]
            )
            to_update._update_capacity_lines()


# XXX: leave request should create forcast negative capacity?
