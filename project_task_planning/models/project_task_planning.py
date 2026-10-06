# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0.en.html).

from odoo import api, fields, models


class ProjectTaskPlanning(models.Model):
    _name = "project.task.planning"
    _description = "Project Task Weekly Planning"
    _order = "allocation_id, date_start"

    allocation_id = fields.Many2one(
        "project.task.allocation",
        string="Task Allocation",
        required=True,
        ondelete="cascade",
    )
    task_id = fields.Many2one(
        related="allocation_id.task_id", string="Task", store=True, readonly=True
    )
    project_id = fields.Many2one(
        related="allocation_id.project_id", string="Project", store=True, readonly=True
    )
    employee_id = fields.Many2one(
        related="allocation_id.employee_id",
        string="Employee",
        store=True,
        readonly=True,
    )

    bucket_id = fields.Many2one(
        "project.bucket",
        string="Planning Bucket",
        required=True,
        ondelete="restrict",
    )
    bucket = fields.Char(
        related="bucket_id.name",
        store=True,
        string="Planning Bucket Name",
    )
    date_start = fields.Date(
        related="bucket_id.date_start",
        store=True,
        string="Start Date",
    )
    date_end = fields.Date(
        related="bucket_id.date_end",
        store=True,
        string="End Date",
    )

    employee_bucket_id = fields.Many2one(
        "hr.employee.bucket",
        string="Employee Capacity Bucket",
        compute="_compute_employee_bucket_id",
        store=True,
    )

    planned_hours = fields.Float(digits=(16, 2))
    blocked = fields.Boolean(
        default=False,
        help="Indicates if the planning entry is blocked from further modifications.",
    )

    _allocation_bucket_uniq = models.Constraint(
        "UNIQUE(allocation_id, bucket_id)",
        (
            "An employee can only have one planning entry per bucket for the "
            "same task allocation."
        ),
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("bucket_id") and vals.get("date_start"):
                date_start = fields.Date.to_date(vals["date_start"])
                bucket = self.env["project.bucket"]._get_or_create_bucket(date_start)
                vals["bucket_id"] = bucket.id
        records = super().create(vals_list)
        records._sync_allocation_dates()
        return records

    def write(self, vals):
        if not vals.get("bucket_id") and vals.get("date_start"):
            date_start = fields.Date.to_date(vals["date_start"])
            bucket = self.env["project.bucket"]._get_or_create_bucket(date_start)
            vals["bucket_id"] = bucket.id

        old_allocs = self.mapped("allocation_id")
        res = super().write(vals)
        if "planned_hours" in vals or "allocation_id" in vals or "bucket_id" in vals:
            self._sync_allocation_dates()
            if "allocation_id" in vals:
                old_allocs._sync_allocation_dates_from_alloc()
        return res

    def unlink(self):
        allocs = self.mapped("allocation_id")
        res = super().unlink()
        allocs._sync_allocation_dates_from_alloc()
        return res

    def _sync_allocation_dates(self):
        allocs = self.mapped("allocation_id")
        allocs._sync_allocation_dates_from_alloc()

    @api.depends("employee_id", "bucket_id")
    def _compute_employee_bucket_id(self):
        for planning in self:
            if planning.employee_id and planning.bucket_id:
                bucket_rec = self.env["hr.employee.bucket"].search(
                    [
                        ("employee_id", "=", planning.employee_id.id),
                        ("bucket_id", "=", planning.bucket_id.id),
                    ],
                    limit=1,
                )
                planning.employee_bucket_id = bucket_rec
            else:
                planning.employee_bucket_id = False

    @api.depends("employee_id", "bucket", "planned_hours")
    def _compute_display_name(self):
        for record in self:
            emp = record.employee_id.name or "N/A"
            bkt = record.bucket or "N/A"
            record.display_name = f"{emp} - {bkt} ({record.planned_hours:.2f}h)"
