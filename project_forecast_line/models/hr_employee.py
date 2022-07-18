# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class HrJob(models.Model):
    _inherit = "hr.job"

    role_id = fields.Many2one("forecast.role")


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    role_ids = fields.One2many("hr.employee.forecast.role", "employee_id")
    main_role_id = fields.Many2one("forecast.role", compute="_compute_main_role_id")

    def _compute_main_role_id(self):
        # can"t store as it depends on current date
        today = fields.Date.context_today(self)
        for rec in self:
            rec.main_role_id = rec.role_ids.filtered(
                lambda r: r.date_start <= today
                and not r.date_end
                or r.date_end >= today
            )[:1].role_id

    def write(self, values):
        values = self._check_job_role(values)
        return super().write(values)

    @api.model_create_multi
    @api.returns("self", lambda value: value.id)
    def create(self, values):
        values = [self._check_job_role(val) for val in values]
        return super().create(values)

    def _check_job_role(self, values):
        """helper method
        ensures that you get a role when you set a job with a role"""
        new_job_id = values.get("job_id")
        if new_job_id:
            job = self.env["hr.job"].browse(new_job_id)
            if job.role_id and "role_ids" not in values:
                values = values.copy()
                values["role_ids"] = [
                    fields.Command.clear(),
                    fields.Command.create({"role_id": job.role_id.id}),
                ]
        return values


class HrEmployeeForecastRole(models.Model):
    _name = "hr.employee.forecast.role"
    _description = "Employee forecast role"
    _order = "employee_id, date_start, sequence, rate DESC, id"

    employee_id = fields.Many2one("hr.employee", required=True, ondelete="cascade")
    role_id = fields.Many2one("forecast.role", required=True)
    date_start = fields.Date(required=True, default=fields.Date.today)
    date_end = fields.Date()
    rate = fields.Integer(default=100)
    sequence = fields.Integer()
    company_id = fields.Many2one(related="employee_id.company_id", store=True)
    # TODO:
    # ensure sum of rate = 100

    @api.model_create_multi
    def create(self, vals_list):
        recs = super().create(vals_list)
        recs._update_forecast_lines()
        return recs

    def write(self, values):
        res = super().write(values)
        self._update_forecast_lines()
        return res

    def _update_forecast_lines(self):
        today = fields.Date.context_today(self)
        ForecastLine = self.env["forecast.line"].sudo()
        if not self:
            return ForecastLine
        leaves = self.env["hr.leave"].search(
            [
                ("employee_id", "in", self.mapped("employee_id").ids),
                ("state", "!=", "cancel"),
                ("date_to", ">=", min(self.mapped("date_start"))),
            ]
        )
        leaves._update_forecast_lines()
        forecast_vals = []
        ForecastLine.search(
            [("res_id", "in", self.ids), ("res_model", "=", self._name)]
        ).unlink()
        horizon_end = ForecastLine._company_horizon_end()
        for rec in self:
            if rec.date_end:
                date_end = rec.date_end
            else:
                date_end = horizon_end - relativedelta(days=1)
            date_start = max(rec.date_start, today)
            resource = rec.employee_id.resource_id
            calendar = resource.calendar_id

            forecast = ForecastLine._number_of_hours(
                date_start,
                date_end + relativedelta(days=1),
                resource,
                calendar,
            )
            forecast_vals += ForecastLine.prepare_forecast_lines(
                name="Employee %s as %s (%d%%)"
                % (rec.employee_id.name, rec.role_id.name, rec.rate),
                date_from=rec.date_start,
                date_to=date_end,
                forecast_hours=forecast * rec.rate / 100.0,
                unit_cost=rec.employee_id.timesheet_cost,  # XXX to check
                ttype="confirmed",
                forecast_role_id=rec.role_id.id,
                employee_id=rec.employee_id.id,
                employee_forecast_role_id=rec.id,
                res_model=self._name,
                res_id=rec.id,
            )

        return ForecastLine.create(forecast_vals)

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
                    "|",
                    ("date_end", "=", False),
                    ("date_end", ">=", today),
                    ("company_id", "=", company.id),
                ]
            )
            to_update._update_forecast_lines()
