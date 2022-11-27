# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging
import random

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ProjectTask(models.Model):
    _inherit = "project.task"

    forecast_role_id = fields.Many2one("forecast.role", ondelete="restrict")
    forecast_date_planned_start = fields.Date("Planned start date")
    forecast_date_planned_end = fields.Date("Planned end date")
    forecast_recomputation_trigger = fields.Float(
        compute="_compute_forecast_recomputation_trigger",
        store=True,
        help="Technical field used to trigger the forecast recomputation",
    )

    @api.model_create_multi
    def create(self, vals_list):
        # compatibility with fields from project_enterprise
        for vals in vals_list:
            if vals.get("planned_date_begin"):
                vals["forecast_date_planned_start"] = vals["planned_date_begin"]
            if vals.get("planned_date_end"):
                vals["forecast_date_planned_end"] = vals["planned_date_end"]
        tasks = super().create(vals_list)
        # tasks._update_forecast_lines()
        return tasks

    def _get_forecast_lines(self, domain=None):
        self.ensure_one()
        base_domain = [("res.model", "=", self._name), ("res_id", "=", self.id)]
        if domain is not None:
            base_domain += domain
        return self.env["forecast.line"].search(base_domain)

    def _update_forecast_lines_trigger_fields(self):
        return [
            # "sale_order_line_id",
            "forecast_role_id",
            "forecast_date_planned_start",
            "forecast_date_planned_end",
            "remaining_hours",
            "name",
            # "planned_time",
            "user_ids",
            "project_id.stage_id",
            "project_id.stage_id.forecast_line_type",
        ]

    @api.depends(_update_forecast_lines_trigger_fields)
    def _compute_forecast_recomputation_trigger(self):
        value = random.random()
        _logger.info("TRIGGER %s", self)
        for rec in self:
            rec.forecast_recomputation_trigger = value

    def write(self, values):
        # compatibility with fields from project_enterprise
        if "planned_date_begin" in values:
            values["forecast_date_planned_start"] = values["planned_date_begin"]
        if "planned_date_end" in values:
            values["forecast_date_planned_end"] = values["planned_date_end"]
        return super().write(values)

    def _write(self, values):
        res = super()._write(values)
        if "forecast_recomputation_trigger" in values:
            self._update_forecast_lines()
        return res

    @api.onchange("user_ids")
    def onchange_user_ids(self):
        for task in self:
            if not task.user_ids:
                continue
            if task.forecast_role_id:
                continue
            employees = task.mapped("user_ids.employee_id")
            for employee in employees:
                if employee.main_role_id:
                    task.forecast_role_id = employee.main_role_id
                    break

    def _get_task_employees(self):
        return self.with_context(active_test=False).mapped("user_ids.employee_id")

    def _update_forecast_lines(self):
        today = fields.Date.context_today(self)
        forecast_vals = []
        ForecastLine = self.env["forecast.line"].sudo()
        # # XXX try to be smarter and only unlink those needing unlinking, update the others
        # #self.flush() # required to make tests pass WTF
        # fl = ForecastLine.search(
        #     [("res_id", "in", self.ids), ("res_model", "=", self._name)]
        # )
        # print('unlink', fl)
        # fl.unlink()
        # fl.flush() # required to make tests pass WTF
        task_with_lines_to_clean = []
        for task in self:
            if not task.forecast_role_id:
                _logger.info("skip task %s: no forecast role", task)
                task_with_lines_to_clean.append(task.id)
                continue
            elif task.project_id.stage_id:
                forecast_type = task.project_id.stage_id.forecast_line_type
                if not forecast_type:
                    _logger.info("skip task %s: no forecast for project state", task)
                    task_with_lines_to_clean.append(task.id)
                    continue  # closed / cancelled stage
            elif task.sale_line_id:
                sale_state = task.sale_line_id.state
                if sale_state == "cancel":
                    _logger.info("skip task %s: cancelled sale", task)
                elif sale_state == "sale":
                    forecast_type = "confirmed"
                else:
                    # no forecast line for cancelled sales
                    #
                    # TODO have forecast quantity if the sale is in Draft and we
                    # are not generating forecast lines from SO
                    _logger.info("skip task %s: draft sale")
                    task_with_lines_to_clean.append(task.id)
                    continue

            if (
                not task.forecast_date_planned_start
                or not task.forecast_date_planned_end
            ):
                _logger.info("skip task %s: no planned dates", task)
                task_with_lines_to_clean.append(task.id)
                continue
            if not task.remaining_hours:
                _logger.info("skip task %s: no remaining hours", task)
                continue
            if task.remaining_hours < 0:
                _logger.info("skip task %s: negative remaining hours", task)
                task_with_lines_to_clean.append(task.id)
                continue
            date_start = max(today, task.forecast_date_planned_start)
            date_end = max(today, task.forecast_date_planned_end)
            employee_ids = task._get_task_employees().ids
            if not employee_ids:
                employee_ids = [False]
            _logger.debug(
                "compute forecast for task %s: %s to %s %sh",
                task,
                date_start,
                date_end,
                task.remaining_hours,
            )
            forecast_hours = task.remaining_hours / len(employee_ids)
            ForecastLine.search(
                [
                    ("res_model", "=", self._name),
                    ("res_id", "=", task.id),
                    ("employee_id", "not in", tuple(employee_ids)),
                ]
            ).unlink()
            for employee_id in employee_ids:
                employee_lines = ForecastLine.search(
                    [
                        ("res_model", "=", self._name),
                        ("res_id", "=", task.id),
                        ("employee_id", "=", employee_id),
                    ]
                )
                forecast_vals += employee_lines._update_forecast_lines(
                    name=task.name,
                    date_from=date_start,
                    date_to=date_end,
                    ttype=forecast_type,
                    forecast_hours=-1 * forecast_hours,
                    # XXX currency + unit conversion
                    unit_cost=task.sale_line_id.product_id.standard_price,
                    forecast_role_id=task.forecast_role_id.id,
                    sale_line_id=task.sale_line_id.id,
                    task_id=task.id,
                    project_id=task.project_id.id,
                    employee_id=employee_id,
                    res_model=self._name,
                    res_id=task.id,
                )
        if task_with_lines_to_clean:
            to_clean = ForecastLine.search(
                [
                    ("res_model", "=", self._name),
                    ("res_id", "in", tuple(task_with_lines_to_clean)),
                ]
            )
            if to_clean:
                to_clean.unlink()
        lines = ForecastLine.create(forecast_vals)
        return lines

    @api.model
    def _recompute_forecast_lines(self, force_company_id=None):
        today = fields.Date.context_today(self)
        if force_company_id:
            companies = self.env["res.company"].browse(force_company_id)
        else:
            companies = self.env["res.company"].search([])
        for company in companies:
            to_update = self.with_company(company).search(
                [
                    ("forecast_date_planned_end", ">=", today),
                    ("company_id", "=", company.id),
                ]
            )
            to_update._update_forecast_lines()
