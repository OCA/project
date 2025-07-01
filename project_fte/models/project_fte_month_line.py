# Copyright 2025 APSL Nagarro
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date, timedelta

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models

MSG_NO_EXEC = _(
    "<p>This project has <b>%(fixed)s&nbsp;fixed hours</b> for the month.</p>"
    "<p>The first <b>%(fixed)s&nbsp;hours</b> recorded are considered fixed hours "
    "and <b>do not count</b> toward the FTE execution percentage.</p>"
    "<p>The execution percentage will start being calculated once "
    "those fixed hours have been exceeded.</p>"
)

MSG_WITH_EXEC = _(
    "<p>This project has <b>%(fixed)s&nbsp;fixed hours</b> for the month.</p>"
    "<p>A total of <b>%(total)s&nbsp;hours</b> have been recorded:</p>"
    "<ul>"
    "<li><b>%(fixed)s&nbsp;hours</b> are considered fixed hours.</li>"
    "<li><b>%(fte)s&nbsp;hours</b> are additional hours that count as FTE hours "
    "and are used to calculate the execution percentage.</li>"
    "</ul>"
)


class FteMonthLine(models.Model):
    _name = "project.fte.month.line"
    _description = "Project FTE Month Line"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "year desc, month desc"

    project_id = fields.Many2one(
        comodel_name="project.project",
        string="Project",
        required=True,
        ondelete="cascade",
    )
    name = fields.Char(compute="_compute_name", store=True)
    month = fields.Selection(
        selection=[
            ("1", "January"),
            ("2", "February"),
            ("3", "March"),
            ("4", "April"),
            ("5", "May"),
            ("6", "June"),
            ("7", "July"),
            ("8", "August"),
            ("9", "September"),
            ("10", "October"),
            ("11", "November"),
            ("12", "December"),
        ],
        required=True,
    )
    year = fields.Integer(required=True, default=lambda self: fields.Date.today().year)
    profile_distribution_ids = fields.One2many(
        comodel_name="project.fte.profile.distribution",
        inverse_name="month_line_id",
        string="Profile Distribution",
    )
    fte_hours = fields.Float(
        string="Total FTE Hours",
        compute="_compute_fte_hours",
        store=True,
        help="Total contracted hours for this month.",
    )
    fixed_hours = fields.Float()
    fixed_hours_cost = fields.Float()

    month_int = fields.Integer(
        string="Month Number",
        compute="_compute_month_int",
        store=True,
        help="Numeric value of the month for proper sorting.",
    )

    executed_hours = fields.Float(
        compute="_compute_executed_hours",
        store=True,
        help="Total hours logged in timesheets for this month.",
    )
    executed_percent = fields.Float(
        compute="_compute_executed_percent",
        store=True,
        help="Percentage of executed hours compared to FTE hours.",
        digits=(16, 2),
    )

    warning_sent = fields.Boolean(string="Execution Warning Sent", default=False)
    overload_sent = fields.Boolean(string="Execution Overload Sent", default=False)
    high_usage_sent = fields.Boolean(string="Execution High Usage Sent", default=False)
    currency_id = fields.Many2one(
        related="project_id.currency_id", string="Currency", readonly=True
    )
    monthly_amount = fields.Monetary(
        compute="_compute_monthly_amount",
        store=True,
        help="Total monetary amount for this month's FTE.",
        currency_field="currency_id",
    )

    fte_line_message = fields.Html(compute="_compute_fte_line_message", store=False)

    @api.depends("month")
    def _compute_month_int(self):
        for line in self:
            line.month_int = int(line.month) if line.month else 0

    _sql_constraints = [
        (
            "project_month_year_uniq",
            "unique(project_id, month, year)",
            "A line for this month and year already exists for this project.",
        )
    ]

    @api.depends("month", "year")
    def _compute_name(self):
        for line in self:
            if line.month and line.year:
                month_str = dict(self._fields["month"].selection).get(line.month)
                line.name = f"{month_str} {line.year}"
            else:
                line.name = _("New")

    @api.depends("profile_distribution_ids.profile_hours")
    def _compute_fte_hours(self):
        for line in self:
            line.fte_hours = sum(line.profile_distribution_ids.mapped("profile_hours"))

    def unlink(self):
        affected_projects = self.mapped("project_id")
        res = super().unlink()

        for project in affected_projects:
            remaining = self.search_count([("project_id", "=", project.id)])
            if remaining == 0:
                project.previous_monthly_hours = False

        return res

    @api.depends("project_id", "month", "year", "fixed_hours")
    def _compute_executed_hours(self):
        AnalyticLine = self.env["account.analytic.line"]

        for line in self:
            line.executed_hours = 0.0
            if not line.project_id or not line.month or not line.year:
                continue

            start_date = date(int(line.year), int(line.month), 1)
            end_date = (start_date + relativedelta(months=1)) - timedelta(days=1)

            domain = [
                ("project_id", "=", line.project_id.id),
                ("date", ">=", start_date),
                ("date", "<=", end_date),
                ("non_billable", "=", False),
            ]

            hours = sum(AnalyticLine.search(domain).mapped("unit_amount"))
            if line.fixed_hours and hours < line.fixed_hours:
                continue
            hours -= line.fixed_hours
            line.executed_hours = hours

    @api.depends("executed_hours", "fte_hours", "fixed_hours")
    def _compute_executed_percent(self):
        for line in self:
            if line.fte_hours:
                line.executed_percent = (line.executed_hours / line.fte_hours) * 100
            else:
                line.executed_percent = 0.0

    @api.depends("profile_distribution_ids", "project_id.discount")
    def _compute_monthly_amount(self):
        for line in self:
            total = 0.0
            for profile in line.profile_distribution_ids:
                total += profile.profile_hours * profile.profile_price_hour

            if line.fixed_hours:
                total += line.fixed_hours_cost * line.fixed_hours

            if line.project_id.discount:
                total -= total * line.project_id.discount

            line.monthly_amount = total

    @api.depends("fixed_hours", "executed_hours")
    def _compute_fte_line_message(self):
        for line in self:
            if not line.fixed_hours:
                line.fte_line_message = ""
                continue

            total_recorded = (line.executed_hours or 0.0) + line.fixed_hours

            if not line.executed_hours:
                line.fte_line_message = _(MSG_NO_EXEC) % {"fixed": line.fixed_hours}
            else:
                line.fte_line_message = _(MSG_WITH_EXEC) % {
                    "fixed": line.fixed_hours,
                    "total": total_recorded,
                    "fte": line.executed_hours,
                }

    @api.model
    def _cron_check_fte_execution(self):
        today = date.today()
        current_month = today.month
        current_year = today.year
        is_mid_month = today.day >= 15

        lines = self.search(
            [
                ("month", "=", str(current_month)),
                ("year", "=", current_year),
            ]
        )

        template_low = self.env.ref("project_fte.mail_template_fte_execution_warning")
        template_high = self.env.ref("project_fte.mail_template_fte_execution_overload")

        for line in lines:
            percent = line.executed_percent or 0.0
            project = line.project_id
            user = project.user_id

            if not user or not user.email:
                continue

            # Warning when execution is below 50% at mid-month
            if is_mid_month and percent < 50 and not line.warning_sent:
                template_low.send_mail(line.id, force_send=True)
                line.warning_sent = True
                continue

            # Warning when execution exceeds 100%
            if percent > 100 and not line.overload_sent:
                template_high.send_mail(line.id, force_send=True)
                line.overload_sent = True
                continue

            # Warning when execution is above 75% at mid-month
            if (
                is_mid_month
                and percent > 75
                and not line.high_usage_sent
                and not line.overload_sent
            ):
                template_high.send_mail(line.id, force_send=True)
                line.high_usage_sent = True

    def action_view_timesheets(self):
        self.ensure_one()
        start_date = date(int(self.year), int(self.month), 1)
        end_date = (start_date + relativedelta(months=1)) - timedelta(days=1)

        action = self.env["ir.actions.act_window"]._for_xml_id(
            "hr_timesheet.timesheet_action_all"
        )
        action.update(
            {
                "domain": [
                    ("project_id", "=", self.project_id.id),
                    ("date", ">=", start_date),
                    ("date", "<=", end_date),
                    ("non_billable", "=", False),
                ],
                "context": {"default_project_id": self.project_id.id},
            }
        )
        return action
