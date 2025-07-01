# Copyright 2025 APSL Nagarro
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class Project(models.Model):
    _inherit = "project.project"

    fte_month_line_ids = fields.One2many(
        comodel_name="project.fte.month.line",
        inverse_name="project_id",
        string="FTE Month Lines",
    )

    previous_monthly_hours = fields.Float(
        help="Used to validate that new profile distributions "
        "match previous monthly allocations.",
    )

    discount = fields.Float(
        string="Discount (%)",
        default=0.0,
        help="Percentage discount applied to the total amount.",
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        related="company_id.currency_id",
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

    monthly_raw_amount = fields.Monetary(
        compute="_compute_monthly_amount",
        store=True,
        help="Total raw monthly amount before discount.",
        currency_field="currency_id",
    )
    monthly_amount = fields.Monetary(
        compute="_compute_monthly_amount",
        store=True,
        help="Total montlhy amount",
        currency_field="currency_id",
    )
    monthly_discount_amount = fields.Monetary(
        compute="_compute_monthly_amount",
        store=True,
        help="Total monthly discount amount",
        currency_field="currency_id",
    )

    fixed_hours = fields.Float()
    fixed_hours_cost = fields.Float()

    allocated_hours = fields.Float(
        compute="_compute_allocated_hours",
        store=True,
        readonly=False,
    )

    monthly_html_table = fields.Html(
        string="Monthly FTE Breakdown",
        compute="_compute_monthly_html_table",
        sanitize=False,
        store=True,
        readonly=True,
    )

    fte_months = fields.Float(
        string="FTE Months",
        compute="_compute_fte_months",
        store=True,
        help="Number of months for which FTE lines will be generated.",
        default=0.0,
    )

    is_fte_closed = fields.Boolean(default=False)

    @api.depends(
        "fte_month_line_ids", "fte_month_line_ids.profile_distribution_ids", "discount"
    )
    def _compute_monthly_html_table(self):
        for project in self:
            lines = project.fte_month_line_ids
            if not lines:
                project.monthly_html_table = ""
                continue

            line = sorted(lines, key=lambda line: (int(line.year), int(line.month)))[0]
            currency = project.currency_id.symbol or "€"
            monthly_hours = project.previous_monthly_hours or 0.0

            row_lines = []
            month_total = 0.0

            ordered_dists = sorted(
                line.profile_distribution_ids,
                key=lambda d: d.profile_hours_percentage,
                reverse=True,
            )

            for dist in ordered_dists:
                hours = monthly_hours * dist.profile_hours_percentage
                amount = hours * dist.profile_price_hour
                month_total += amount
                row_lines.append(
                    f"""
                    <tr>
                        <td>{dist.role_id.name}</td>
                        <td>{dist.profile_price_hour:.2f} {currency}</td>
                        <td>{hours:.2f}</td>
                        <td>{dist.profile_hours_percentage * 100:.2f}%</td>
                        <td>{amount:,.2f} {currency}</td>
                    </tr>
                """
                )
            if project.fixed_hours > 0:
                fixed_amount = project.fixed_hours * line.fixed_hours_cost
                month_total += fixed_amount
                row_lines.append(
                    f"""
                    <tr>
                        <td>Fixed Hours</td>
                        <td>{line.fixed_hours_cost:.2f} {currency}</td>
                        <td>{project.fixed_hours:.2f}</td>
                        <td>--</td>
                        <td>{fixed_amount:,.2f} {currency}</td>
                    </tr>
                """
                )

            discount_amount = month_total * (project.discount or 0.0)
            final = month_total - discount_amount

            header = """
                <tr>
                    <th>Profile</th>
                    <th>Hourly Rate</th>
                    <th>Monthly Hours</th>
                    <th>Distribution (%)</th>
                    <th>Amount</th>
                </tr>
            """

            row_lines.append(
                f"""
                <tr>
                    <td colspan="2" align="right">
                        <strong>Total</strong>
                    </td>
                    <td>
                        <strong>{monthly_hours:.2f}</strong>
                    </td>
                    <td>
                        <strong>100%</strong>
                    </td><td>
                        <strong>{month_total:,.2f} {currency}</strong>
                    </td>
                </tr>
                """
            )

            if project.discount > 0.0:
                row_lines.append(
                    f"""
                    <tr>
                        <td colspan="3" align="right">
                            Discount
                        </td>
                        <td>
                            {project.discount * 100:.0f}%
                        </td>
                        <td>
                            {discount_amount:,.2f} {currency}
                        </td>
                    </tr>
                    """
                )
            row_lines.append(
                f"""
                <tr>
                    <td align="right" colspan="4">
                        <strong>
                            Cost
                        </strong>
                    </td>
                    <td>
                        <strong>{final:,.2f} {currency}</strong>
                    </td>
                </tr>
                <tr>
                    <td align="right" colspan="4">
                        <strong>
                            Months
                        </strong>
                    </td>
                    <td>
                        <strong>{project.fte_months}</strong>
                    </td>
                </tr>
                """
            )

            project.monthly_html_table = f"""
                <table class="table table-sm table-bordered"
                style="width:100%; margin-bottom:20px">
                    <thead>{header}</thead>
                    <tbody>{''.join(row_lines)}</tbody>
                </table>
            """

    @api.depends("fte_month_line_ids", "discount")
    def _compute_total_amount(self):
        for project in self:
            total_amount = 0.0
            discount_amount = 0.0
            fixed_total = 0.0
            for month_line in project.fte_month_line_ids:
                fixed_total += month_line.fixed_hours_cost * month_line.fixed_hours
                for dist in month_line.profile_distribution_ids:
                    total_amount += dist.profile_hours * dist.profile_price_hour
            project.total_raw_amount = total_amount + fixed_total
            discount_amount = project.discount * project.total_raw_amount
            project.total_amount = project.total_raw_amount - discount_amount
            project.discount_amount = discount_amount

    @api.depends("fte_month_line_ids", "discount")
    def _compute_monthly_amount(self):
        for project in self:
            monthly_raw_amount = 0.0
            monthly_amount = 0.0
            monthly_discount_amount = 0.0
            fixed_total = 0.0

            if project.fte_month_line_ids and project.previous_monthly_hours:
                first_line = project.fte_month_line_ids.sorted(
                    key=lambda line: (int(line.year), int(line.month))
                )[0]

                monthly_hours = project.previous_monthly_hours

                for line in first_line.profile_distribution_ids:
                    hours = monthly_hours * line.profile_hours_percentage
                    monthly_raw_amount += hours * line.profile_price_hour

                fixed_total = first_line.fixed_hours_cost * first_line.fixed_hours
                monthly_discount_amount = monthly_raw_amount * project.discount
                monthly_amount = monthly_raw_amount - monthly_discount_amount
            project.monthly_raw_amount = monthly_raw_amount + fixed_total
            project.monthly_amount = monthly_amount + fixed_total
            project.monthly_discount_amount = monthly_discount_amount

    @api.depends(
        "fte_month_line_ids.profile_distribution_ids.profile_hours",
        "fte_month_line_ids",
    )
    def _compute_allocated_hours(self):
        for project in self:
            allocated_hours = sum(
                dist.profile_hours
                for month_line in project.fte_month_line_ids
                for dist in month_line.profile_distribution_ids
            )
            project.allocated_hours = allocated_hours

    @api.depends(
        "fte_month_line_ids", "fte_month_line_ids.fte_hours", "previous_monthly_hours"
    )
    def _compute_fte_months(self):
        for project in self:
            total_hours = sum(project.fte_month_line_ids.mapped("fte_hours"))
            if project.previous_monthly_hours > 0:
                project.fte_months = round(
                    total_hours / project.previous_monthly_hours, 2
                )
            else:
                project.fte_months = 0.0

    def action_copy_last_fte_line(self):
        self.ensure_one()
        sorted_fte_lines = self.fte_month_line_ids.sorted(
            key=lambda line: (int(line.year), int(line.month)), reverse=True
        )
        last_fte_line = sorted_fte_lines[0]
        current_month = int(last_fte_line.month)
        next_month = current_month + 1 if current_month < 12 else 1
        year = last_fte_line.year if next_month > 1 else last_fte_line.year + 1

        new_line = last_fte_line.copy(
            default={
                "month": str(next_month),
                "project_id": last_fte_line.project_id.id,
                "fte_hours": last_fte_line.fte_hours,
                "year": year,
            }
        )

        new_distributions = last_fte_line.profile_distribution_ids.mapped(
            lambda dist: {
                "role_id": dist.role_id.id,
                "profile_hours": dist.profile_hours,
                "profile_price_hour": dist.profile_price_hour,
            }
        )
        new_line.profile_distribution_ids = [(0, 0, vals) for vals in new_distributions]

        return True

    def action_delete_fte(self):
        self.ensure_one()
        if not self.fte_month_line_ids:
            return True

        # Eliminate all FTE month lines and their distributions
        for line in self.fte_month_line_ids:
            line.profile_distribution_ids.unlink()
        self.fte_month_line_ids.unlink()

        return True

    def action_close_fte(self):
        self.ensure_one()
        self.is_fte_closed = True
        return True

    def action_reopen_fte(self):
        self.ensure_one()
        self.is_fte_closed = False
        return True
