# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0.en.html).

from datetime import timedelta

from odoo import api, fields, models


class ProjectBucket(models.Model):
    _name = "project.bucket"
    _description = "Planning Bucket"
    _order = "date_start desc"

    name = fields.Char(string="Bucket Name", required=True)
    date_start = fields.Date(string="Start Date", required=True)
    date_end = fields.Date(string="End Date", required=True)
    bucket_type = fields.Selection(
        [("daily", "Daily"), ("weekly", "Weekly"), ("monthly", "Monthly")],
        required=True,
    )

    _name_uniq = models.Constraint(
        "UNIQUE(name)",
        "The bucket name must be unique.",
    )

    relative_index = fields.Integer(
        compute="_compute_relative_index",
        search="_search_relative_index",
        help=(
            "Chronological distance from the current period (0 for today's "
            "period, positive for future, negative for past)."
        ),
    )

    def _compute_relative_index(self):
        today = fields.Date.context_today(self)
        for record in self:
            if not record.date_start or not record.bucket_type:
                record.relative_index = 0
                continue
            today_start = self._get_bucket_start_date(today, record.bucket_type)
            if record.bucket_type == "daily":
                record.relative_index = (record.date_start - today_start).days
            elif record.bucket_type == "monthly":
                record.relative_index = (
                    record.date_start.year - today_start.year
                ) * 12 + (record.date_start.month - today_start.month)
            else:  # weekly
                record.relative_index = (record.date_start - today_start).days // 7

    @api.model
    def _search_relative_index(self, operator, value):
        bucket_type = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("project_task_planning.planning_bucket", "weekly")
        )
        today = fields.Date.context_today(self)
        today_start = self._get_bucket_start_date(today, bucket_type)
        from dateutil.relativedelta import relativedelta

        if bucket_type == "daily":
            target_date_start = today_start + timedelta(days=value)
        elif bucket_type == "monthly":
            target_date_start = today_start + relativedelta(months=value)
        else:  # weekly
            target_date_start = today_start + timedelta(days=7 * value)
        return [
            ("date_start", operator, target_date_start),
            ("bucket_type", "=", bucket_type),
        ]

    @api.model
    def _get_bucket_start_date(self, date_val, bucket_type):
        if not date_val:
            return False
        if bucket_type == "monthly":
            return date_val.replace(day=1)
        elif bucket_type == "weekly":
            return date_val - timedelta(days=date_val.weekday())
        return date_val  # daily

    @api.model
    def _get_bucket_end_date(self, date_val, bucket_type):
        if not date_val:
            return False
        if bucket_type == "monthly":
            next_month = date_val.replace(day=28) + timedelta(days=4)
            return next_month - timedelta(days=next_month.day)
        elif bucket_type == "weekly":
            return date_val + timedelta(days=6 - date_val.weekday())
        return date_val  # daily

    @api.model
    def _get_or_create_bucket(self, date_val):
        if not date_val:
            return self.browse()

        # 1. Determine active bucket type from system parameter
        bucket_type = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("project_task_planning.planning_bucket", "weekly")
        )

        # 2. Compute date boundaries
        date_start = self._get_bucket_start_date(date_val, bucket_type)
        date_end = self._get_bucket_end_date(date_val, bucket_type)

        # 3. Compute bucket name
        if bucket_type == "daily":
            bucket_name = date_start.strftime("%Y-%m-%d")
        elif bucket_type == "monthly":
            bucket_name = f"{date_start.year}-M{date_start.month:02d}"
        else:  # weekly
            year, week_num, _ = date_start.isocalendar()
            bucket_name = f"{year}-S{week_num:02d}"

        # 4. Find or create the bucket
        bucket = self.search([("name", "=", bucket_name)], limit=1)
        if not bucket:
            bucket = self.create(
                {
                    "name": bucket_name,
                    "date_start": date_start,
                    "date_end": date_end,
                    "bucket_type": bucket_type,
                }
            )
        return bucket
