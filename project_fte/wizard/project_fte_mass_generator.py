# Copyright 2025 APSL Nagarro
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import calendar
import math
from datetime import date, timedelta

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

from ..models.project_fte_month_line import MSG_NO_EXEC


class ProjectFteMassGeneratorProfile(models.TransientModel):
    _name = "project.fte.mass.generator.profile"
    _description = "Profile Distribution for Mass FTE Generator Wizard"

    wizard_id = fields.Many2one(
        comodel_name="project.fte.mass.generator",
        string="FTE Mass Generator Wizard",
        required=True,
        ondelete="cascade",
    )
    role_id = fields.Many2one(
        comodel_name="project.role",
        string="Profile/Role",
        required=True,
    )
    profile_hours = fields.Float(
        required=True,
    )
    profile_hours_percentage = fields.Float(
        string="Percentage",
        compute="_compute_profile_hours_percentage",
        store=True,
        help="Percentage of this profile's hours over the total for the month.",
    )
    profile_price_hour = fields.Float(
        string="Price per Hour",
        compute="_compute_profile_price_hour",
        store=True,
        help="Price per hour for this profile.",
        readonly=False,
    )
    profile_price_amount = fields.Monetary(
        string="Amount",
        compute="_compute_profile_price_amount",
        store=True,
        help="Total cost for this profile in the month.",
        currency_field="currency_id",
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Currency",
        related="wizard_id.project_id.company_id.currency_id",
        store=True,
    )

    @api.depends("profile_hours", "wizard_id.fte_hours")
    def _compute_profile_hours_percentage(self):
        for dist in self:
            total_hours = dist.wizard_id.fte_hours
            if total_hours > 0:
                dist.profile_hours_percentage = (
                    (dist.profile_hours * 100) / total_hours / 100
                )
            else:
                dist.profile_hours_percentage = 0.0

    @api.depends("profile_hours", "profile_price_hour")
    def _compute_profile_price_amount(self):
        for dist in self:
            if dist.profile_hours:
                dist.profile_price_amount = dist.profile_hours * dist.profile_price_hour
            else:
                dist.profile_price_amount = 0.0

    @api.depends("role_id.price_hour")
    def _compute_profile_price_hour(self):
        for dist in self:
            dist.profile_price_hour = dist.role_id.price_hour or 0.0

    @api.constrains("role_id", "wizard_id")
    def _check_duplicate_roles(self):
        for record in self:
            duplicate_roles = self.env["project.fte.mass.generator.profile"].search(
                [
                    ("wizard_id", "=", record.wizard_id.id),
                    ("role_id", "=", record.role_id.id),
                    ("id", "!=", record.id),
                ]
            )
            if duplicate_roles:
                raise UserError(
                    _(
                        "The role '%s' has already been selected, please"
                        " choose another one"
                    )
                    % record.role_id.name
                )


class ProjectFteMassGenerator(models.TransientModel):
    _name = "project.fte.mass.generator"
    _description = "Wizard to Mass Generate Project FTE Lines"

    project_id = fields.Many2one(
        comodel_name="project.project",
        string="Project",
        required=True,
        readonly=True,
        default=lambda self: self.env.context.get("active_id"),
    )

    @api.model
    def _default_date_from(self):
        project = False
        if self.env.context.get("active_id"):
            project = self.env["project.project"].browse(self.env.context["active_id"])

        if project:
            FteLine = self.env["project.fte.month.line"]
            existing_lines = FteLine.search([("project_id", "=", project.id)], limit=1)

            if existing_lines and project.date:
                return project.date
            else:
                return project.date_start
        return False

    date_from = fields.Date(
        string="Start Date", required=True, default=_default_date_from
    )
    date_to = fields.Date(string="End Date", compute="_compute_date_to", store=True)
    profile_distribution_ids = fields.One2many(
        comodel_name="project.fte.mass.generator.profile",
        inverse_name="wizard_id",
        string="Profile Distribution",
    )
    overwrite_existing = fields.Boolean(
        string="Overwrite Existing Lines",
        help="If checked, any existing FTE lines for "
        "the selected months will be deleted and recreated.",
    )
    fte_hours = fields.Float(
        string="Total FTE Hours",
        required=True,
        store=True,
        help="""Total FTE hours to allocate for the project.""",
    )
    monthly_hours = fields.Float(store=True)
    discount = fields.Float(
        string="Discount (%)",
        default=0.0,
        help="Percentage discount applied to the total amount.",
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        related="project_id.company_id.currency_id",
        store=True,
    )
    total_raw_amount = fields.Monetary(
        compute="_compute_total_amount",
        store=True,
        help="Total raw amount before applying the discount.",
        currency_field="currency_id",
    )
    total_amount = fields.Monetary(
        compute="_compute_total_amount",
        store=True,
        help="Total amount",
        currency_field="currency_id",
    )
    discount_amount = fields.Monetary(
        compute="_compute_total_amount",
        store=True,
        help="Total discount amount applied to the total.",
        currency_field="currency_id",
    )
    month_raw_amount = fields.Monetary(
        compute="_compute_month_amount",
        store=True,
        help="Total raw amount per month before discount.",
        currency_field="currency_id",
    )
    month_amount = fields.Monetary(
        compute="_compute_month_amount",
        store=True,
        help="Total amount per month.",
        currency_field="currency_id",
    )
    month_discount_amount = fields.Monetary(
        compute="_compute_month_amount",
        store=True,
        help="Total discount amount per month.",
        currency_field="currency_id",
    )
    fixed_hours = fields.Float()
    fixed_hours_cost = fields.Float()
    fixed_hours_total = fields.Monetary(
        compute="_compute_fixed_hours_total",
        store=True,
        help="Total amount for fixed hours.",
        currency_field="currency_id",
    )

    fte_months = fields.Float(
        string="FTE Months",
        compute="_compute_fte_months",
        store=True,
        help="Number of months for which FTE lines will be generated.",
        default=0.0,
    )

    fte_message = fields.Html(compute="_compute_fte_message", store=False)

    @api.depends(
        "profile_distribution_ids.profile_price_amount", "discount", "fixed_hours_total"
    )
    def _compute_total_amount(self):
        for wizard in self:
            total_amount = sum(
                line.profile_price_amount for line in wizard.profile_distribution_ids
            )
            fixed_total = wizard.fixed_hours_total * wizard.fte_months
            wizard.total_raw_amount = total_amount + fixed_total
            discounted_amount = wizard.discount * wizard.total_raw_amount
            total_amount = wizard.total_raw_amount - discounted_amount
            wizard.discount_amount = discounted_amount
            wizard.total_amount = total_amount

    @api.depends(
        "profile_distribution_ids.profile_price_amount",
        "total_amount",
        "monthly_hours",
        "discount",
        "fixed_hours_total",
    )
    def _compute_month_amount(self):
        for wizard in self:
            raw_month_total = 0.0
            for line in wizard.profile_distribution_ids:
                raw_month_total += (
                    wizard.monthly_hours
                    * line.profile_hours_percentage
                    * line.profile_price_hour
                )
            wizard.month_raw_amount = raw_month_total + wizard.fixed_hours_total
            wizard.month_discount_amount = wizard.discount * wizard.month_raw_amount
            wizard.month_amount = wizard.month_raw_amount - wizard.month_discount_amount

    @api.depends("fixed_hours", "fixed_hours_cost")
    def _compute_fixed_hours_total(self):
        for wizard in self:
            if wizard.fixed_hours and wizard.fixed_hours_cost:
                wizard.fixed_hours_total = wizard.fixed_hours * wizard.fixed_hours_cost
            else:
                wizard.fixed_hours_total = 0.0

    @api.depends("fte_hours", "monthly_hours")
    def _compute_fte_months(self):
        for wizard in self:
            if wizard.fte_hours and wizard.monthly_hours:
                wizard.fte_months = round(wizard.fte_hours / wizard.monthly_hours, 2)
            else:
                wizard.fte_months = 0.0

    @api.depends("fixed_hours")
    def _compute_fte_message(self):
        for wizard in self:
            if not wizard.fixed_hours:
                wizard.fte_message = ""
                continue

            wizard.fte_message = _(MSG_NO_EXEC) % {
                "fixed": wizard.fixed_hours,
            }

    @api.depends("date_from", "fte_hours", "monthly_hours", "project_id")
    def _compute_date_to(self):
        for record in self:
            record.date_to = False

            if (
                not record.project_id
                or not record.date_from
                or record.monthly_hours <= 0
            ):
                continue

            start_date_for_calculation = record.date_from
            hours_for_duration = record.fte_hours

            FteLine = self.env["project.fte.month.line"]
            existing_project_lines = FteLine.search(
                [
                    ("project_id", "=", record.project_id.id),
                ],
                limit=1,
            )

            if existing_project_lines:
                if record.project_id.date and record.project_id.date.day != 1:
                    start_date_for_calculation = record.project_id.date + timedelta(
                        days=1
                    )
                    hours_for_duration = record.monthly_hours

            if hours_for_duration <= 0:
                record.date_to = start_date_for_calculation
                continue

            full_months = math.floor(hours_for_duration / record.monthly_hours)

            remaining_hours = hours_for_duration % record.monthly_hours

            calculated_date_to = start_date_for_calculation

            if full_months > 0:
                calculated_date_to += relativedelta(months=full_months)

            if remaining_hours > 0:
                month_fraction = remaining_hours / record.monthly_hours

                days_in_current_month = (
                    date(calculated_date_to.year, calculated_date_to.month, 1)
                    + relativedelta(months=1)
                    - timedelta(days=1)
                ).day

                additional_days = math.ceil(month_fraction * days_in_current_month)

                calculated_date_to += timedelta(days=additional_days)

            if calculated_date_to < start_date_for_calculation:
                record.date_to = start_date_for_calculation
            else:
                record.date_to = calculated_date_to

    def compute_profile_distribution_from_milestones(self):
        self.ensure_one()
        Task = self.env["project.task"]
        role_hours = {}

        tasks = Task.search([("project_id", "=", self.project_id.id)])

        for task in tasks:
            milestone = task.milestone_id
            if not milestone:
                raise UserError(
                    _(
                        """Task '%s' does not have an associated milestone.
                        Please assign a milestone to the task
                        before generating FTE lines from milestones"""
                    )
                    % task.name
                )
            role = milestone.project_role_id
            if not role:
                raise UserError(
                    _(
                        """Milestone '%s' does not have an associated role.
                        Please assign a role to the milestone
                        before generating FTE lines from milestones"""
                    )
                    % milestone.name
                )

            if role.id not in role_hours:
                role_hours[role.id] = {"role": role, "hours": 0.0}
            role_hours[role.id]["hours"] += task.allocated_hours or 0.0

        new_lines = [(5, 0, 0)]

        for __, data in role_hours.items():
            new_lines.append(
                (
                    0,
                    0,
                    {
                        "role_id": data["role"].id,
                        "profile_hours": data["hours"],
                    },
                )
            )

        self.profile_distribution_ids = new_lines
        self.fte_hours = sum(data["hours"] for data in role_hours.values())

        return {
            "type": "ir.actions.act_window",
            "res_model": "project.fte.mass.generator",
            "res_id": self.id,
            "view_mode": "form",
            "view_type": "form",
            "target": "new",
        }

    def _check_required_fields(self):
        if not self.date_from or not self.date_to:
            raise ValidationError(_("Both Start Date and End Date must be set."))

        if self.monthly_hours <= 0:
            raise ValidationError(
                _("Monthly hours to allocate must be greater than zero.")
            )

        total_profile_hours_input = sum(
            line.profile_hours for line in self.profile_distribution_ids
        )
        if total_profile_hours_input <= 0:
            raise ValidationError(
                _("Total monthly hours for profiles must be greater than zero.")
            )

        if self.project_id.previous_monthly_hours:
            if round(total_profile_hours_input, 2) != round(
                self.project_id.previous_monthly_hours, 2
            ):
                raise ValidationError(
                    _(
                        "The total monthly hours for profiles (%(current).2f) "
                        "must match the previously used monthly hours (%(previous).2f) "
                        "in this project."
                    )
                    % {
                        "current": total_profile_hours_input,
                        "previous": self.project_id.previous_monthly_hours,
                    }
                )

    def _check_existing_lines_if_needed(self):
        months_to_check = []
        current_date_check = date(self.date_from.year, self.date_from.month, 1)
        while current_date_check <= self.date_to:
            months_to_check.append(
                (str(current_date_check.month), current_date_check.year)
            )
            current_date_check += relativedelta(months=1)

        FteLine = self.env["project.fte.month.line"]
        lines = FteLine.search(
            [
                ("project_id", "=", self.project_id.id),
                ("year", "in", [m[1] for m in months_to_check]),
            ]
        )

        months_set = set(months_to_check)
        existing_lines = lines.filtered(
            lambda line: (line.month, line.year) in months_set
        )

        if existing_lines:
            overlapping_months = {
                f"{line.month}/{line.year}" for line in existing_lines
            }
            raise UserError(
                _(
                    "Existing FTE lines found for the "
                    "following months: %s. "
                    "Please adjust the date range."
                )
                % ", ".join(sorted(overlapping_months))
            )

    def _compute_lines_to_create_with_limit(self, remaining_hours=None):
        if remaining_hours is None:
            remaining_hours = self.fte_hours
        lines_to_create = []
        total_profile_hours_input = sum(
            line.profile_hours for line in self.profile_distribution_ids
        )

        if total_profile_hours_input <= 0:
            raise ValidationError(_("Total profile hours must be greater than zero."))

        total_hours_to_assign = remaining_hours
        current_date_iterator = date(self.date_from.year, self.date_from.month, 1)

        if remaining_hours < self.fte_hours:
            current_date_iterator += relativedelta(months=1)

        while total_hours_to_assign > 0 and current_date_iterator <= self.date_to:
            month_str = str(current_date_iterator.month)
            year_int = current_date_iterator.year
            effective_start_date = max(
                date(current_date_iterator.year, current_date_iterator.month, 1),
                self.date_from,
            )

            effective_end_date = min(
                date(
                    current_date_iterator.year,
                    current_date_iterator.month,
                    calendar.monthrange(
                        current_date_iterator.year, current_date_iterator.month
                    )[1],
                ),
                self.date_to,
            )

            days_effective_in_month = (
                effective_end_date - effective_start_date
            ).days + 1
            total_days_in_month = calendar.monthrange(
                current_date_iterator.year, current_date_iterator.month
            )[1]

            if days_effective_in_month <= 0:
                current_date_iterator += relativedelta(months=1)
                continue

            proportion_factor = days_effective_in_month / total_days_in_month

            month_hours = round(self.monthly_hours * proportion_factor, 2)

            if month_hours > total_hours_to_assign:
                month_hours = total_hours_to_assign

            profile_vals_list = []
            for dist_line in self.profile_distribution_ids:
                if dist_line.role_id and dist_line.profile_hours > 0:
                    adjusted_hours = (
                        dist_line.profile_hours / total_profile_hours_input
                    ) * month_hours

                    profile_vals_list.append(
                        (
                            0,
                            0,
                            {
                                "role_id": dist_line.role_id.id,
                                "profile_hours": adjusted_hours,
                                "profile_price_hour": dist_line.profile_price_hour,
                            },
                        )
                    )

            lines_to_create.append(
                {
                    "project_id": self.project_id.id,
                    "month": month_str,
                    "year": year_int,
                    "fixed_hours": self.fixed_hours,
                    "fixed_hours_cost": self.fixed_hours_cost,
                    "profile_distribution_ids": profile_vals_list,
                }
            )

            total_hours_to_assign -= month_hours
            current_date_iterator += relativedelta(months=1)

        return lines_to_create

    def update_project_hours_and_dates(self, total_hours_to_assign):
        project = self.project_id

        existing_lines = self.env["project.fte.month.line"].search(
            [("project_id", "=", project.id)], limit=1
        )

        date_vals = {}

        if existing_lines:
            project.allocated_hours += total_hours_to_assign
        else:
            project.allocated_hours = total_hours_to_assign
            date_vals["date_start"] = self.date_from

        if self.date_to:
            date_vals["date"] = self.date_to

        project.write(date_vals)

    def action_generate_lines(self):
        self.ensure_one()

        self._check_required_fields()

        total_hours_to_assign = self.fte_hours

        self.update_project_hours_and_dates(total_hours_to_assign)

        self._check_existing_lines_if_needed()
        total_hours_to_assign = self.fte_hours

        if total_hours_to_assign > 0:
            lines_to_create = self._compute_lines_to_create_with_limit(
                remaining_hours=total_hours_to_assign
            )
            self.env["project.fte.month.line"].create(lines_to_create)
            self.project_id.previous_monthly_hours = self.monthly_hours
            self.project_id.discount = self.discount
            self.project_id.fixed_hours = self.fixed_hours
            self.project_id.fixed_hours_cost = self.fixed_hours_cost
            self.project_id._compute_total_amount()

        return {"type": "ir.actions.act_window_close"}
