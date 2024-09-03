# Copyright 2017 Tecnativa - Carlos Dauden
# Copyright 2021 Open Source Integrators - Daniel Reis
# Copyright 2016-2024 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.sql import column_exists, create_column


class ProjectTask(models.Model):
    _inherit = "project.task"

    planned_date_start = fields.Datetime(
        compute="_compute_planned_date_start",
        store=True,
        readonly=False,
    )
    planned_date_end = fields.Datetime(
        compute="_compute_planned_date_end",
        store=True,
        readonly=False,
    )

    @api.depends("date_assign")
    def _compute_planned_date_start(self):
        """Put the assignation date as the planned start if not other value is
        previously set, avoiding to trigger the constraint.
        """
        for record in self.filtered(
            lambda x: not x.planned_date_start and x.date_assign
        ):
            if (
                not record.planned_date_end
                or record.planned_date_end >= record.date_assign
            ):
                record.planned_date_start = record.date_assign

    @api.depends("date_end")
    def _compute_planned_date_end(self):
        """Put the done date as the planned end if not other value is previously set,
        avoiding to trigger the constraint.
        """
        for record in self.filtered(lambda x: not x.planned_date_end and x.date_end):
            if (
                not record.planned_date_start
                or record.planned_date_start <= record.date_end
            ):
                record.planned_date_end = record.date_end

    @api.constrains("planned_date_start", "planned_date_end")
    def _check_planned_dates(self):
        for task in self:
            if task.planned_date_start and task.planned_date_end:
                if task.planned_date_end < task.planned_date_start:
                    raise ValidationError(
                        _("The end date must be after the start date.")
                    )

    def _auto_init(self):
        # Pre-create and fill planned_date_start and planned_date_end columns for
        # avoiding a costly computation and possible conflicts with the constraint
        cr = self.env.cr
        if not column_exists(cr, "project_task", "planned_date_start"):
            create_column(cr, "project_task", "planned_date_start", "timestamp")
            cr.execute(
                """
                UPDATE project_task
                SET planned_date_start = date_assign
                WHERE planned_date_start IS NULL
                AND date_assign IS NOT NULL
                """
            )
        if not column_exists(cr, "project_task", "planned_date_end"):
            create_column(cr, "project_task", "planned_date_end", "timestamp")
            cr.execute(
                """
                UPDATE project_task
                SET planned_date_end = date_end
                WHERE planned_date_end IS NULL
                AND date_end IS NOT NULL
                AND COALESCE(planned_date_start, date_end) <= date_end
                """
            )
        return super()._auto_init()
