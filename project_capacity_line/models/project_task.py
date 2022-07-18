# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


TRIGGER_FIELDS = {
    "sale_order_line_id",
    "capacity_role_id",
    "capacity_date_planned_start",
    "capacity_date_planned_end",
    "remaining_hours",
    "name",
    "planned_time",
    "user_ids",
}


class ProjectTask(models.Model):
    _inherit = "project.task"

    capacity_role_id = fields.Many2one("capacity.role")
    capacity_date_planned_start = fields.Date("Planned start date")
    capacity_date_planned_end = fields.Date("Planned end date")

    @api.model_create_multi
    def create(self, vals_list):
        # compatibility with fields from project_enterprise
        for vals in vals_list:
            if "planned_date_begin" in vals:
                vals["capacity_date_planned_start"] = vals["planned_date_begin"]
            if "planned_date_end" in vals:
                vals["capacity_date_planned_end"] = vals["planned_date_end"]
        tasks = super().create(vals_list)
        tasks._update_capacity_lines()
        return tasks

    def write(self, values):
        # compatibility with fields from project_enterprise
        if "planned_date_begin" in values:
            values["capacity_date_planned_start"] = values["planned_date_begin"]
        if "planned_date_end" in values:
            values["capacity_date_planned_end"] = values["planned_date_end"]
        res = super().write(values)
        written_fields = set(values.keys())
        if written_fields & TRIGGER_FIELDS:
            self._update_capacity_lines()
        return res

    @api.onchange("user_ids")
    def onchange_user_ids(self):
        for task in self:
            if not task.user_ids:
                continue
            if task.capacity_role_id:
                continue
            employees = task.mapped("user_ids.employee_id")
            for employee in employees:
                if employee.main_role_id:
                    task.capacity_role_id = employee.main_role_id
                    break

    def _update_capacity_lines(self):
        today = fields.Date.context_today(self)
        capacity_vals = []
        CapacityLine = self.env["capacity.line"].sudo()
        # XXX try to be smarter and only unlink those needing unlinking, update the others
        CapacityLine.search(
            [("res_id", "in", self.ids), ("res_model", "=", self._name)]
        ).unlink()
        for task in self:
            if not task.capacity_role_id:
                _logger.info("skip task %s: no capacity role", task)
                continue
            elif task.project_id.stage_id:
                capacity_type = task.project_id.stage_id.capacity_line_type
                if not capacity_type:
                    _logger.info("skip task %s: no capacity for project state", task)
                    continue  # closed / cancelled stage
            elif task.sale_line_id:
                sale_state = task.sale_line_id.state
                if sale_state == "cancel":
                    _logger.info("skip task %s: cancelled sale", task)
                elif sale_state == "sale":
                    capacity_type = "confirmed"
                else:
                    # no capacity line for cancelled sales
                    #
                    # TODO have forecast quantity if the sale is in Draft and we
                    # are not generating capacity lines from SO
                    _logger.info("skip task %s: draft sale")
                    continue
            if (
                not task.capacity_date_planned_start
                or not task.capacity_date_planned_end
            ):
                _logger.info("skip task %s: no planned dates", task)
                continue
            if not task.remaining_hours:
                _logger.info("skip task %s: no remaining hours", task)
                continue
            if task.remaining_hours < 0:
                _logger.info("skip task %s: negative remaining hours", task)
                continue
            date_start = max(today, task.capacity_date_planned_start)
            date_end = max(today, task.capacity_date_planned_end)
            employee_ids = task.mapped("user_ids.employee_id").ids
            if not employee_ids:
                employee_ids = [False]
            _logger.debug(
                "compute capacity for task %s: %s to %s %sh",
                task,
                date_start,
                date_end,
                task.remaining_hours,
            )
            capacity_hours = task.remaining_hours / len(employee_ids)
            for employee_id in employee_ids:
                capacity_vals += CapacityLine.prepare_capacity_lines(
                    name=task.name,
                    date_from=date_start,
                    date_to=date_end,
                    capacity_type=capacity_type,
                    capacity_hours=-1 * capacity_hours,
                    # XXX currency + unit conversion
                    unit_cost=task.sale_line_id.product_id.standard_price,
                    capacity_role_id=task.capacity_role_id.id,
                    sale_line_id=task.sale_line_id.id,
                    task_id=task.id,
                    project_id=task.project_id.id,
                    employee_id=employee_id,
                    res_model=self._name,
                    res_id=task.id,
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
                    ("capacity_date_planned_end", ">=", today),
                    ("company_id", "=", company.id),
                ]
            )
            to_update._update_capacity_lines()
