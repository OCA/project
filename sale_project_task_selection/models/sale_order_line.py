# Copyright 2025 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    is_project_service_tracking_line = fields.Boolean(
        compute="_compute_is_project_service_tracking_line"
    )

    @api.depends("service_tracking")
    def _compute_is_project_service_tracking_line(self):
        for line in self:
            line.is_project_service_tracking_line = line.service_tracking in (
                "task_global_project",
                "task_in_project",
                "project_only",
            )

    @api.onchange("task_id")
    def _onchange_task_set_project_if_empty(self):
        """UX: Onchange task set the project (if empty)"""
        for line in self:
            if line.state not in ("draft", "sent"):  # pragma: no cover
                continue
            if line.task_id and not line.project_id:
                line.project_id = line.task_id.project_id

    @api.onchange("project_id")
    def _onchange_project_clear_task_if_differs(self):
        """UX: Onchange project clear the task (if it differs)"""
        for line in self:
            if line.state not in ("draft", "sent"):  # pragma: no cover
                continue
            if (
                line.project_id
                and line.task_id
                and line.project_id != line.task_id.project_id
            ):
                line.task_id = False

    def _get_so_lines_task_global_project(self):
        # OVERRIDE to ignore lines configured to create a Task in the Quotation project
        # or in a specific project set in the product, if there's already a Project set
        # on the line itself.
        # We should prefer the line's Project over anything else.
        lines = super()._get_so_lines_task_global_project()
        if self.env.context.get("ignore_lines_with_project"):
            lines = lines.filtered(lambda line: not line.project_id)
        return lines

    def _timesheet_service_generation(self):
        # OVERRIDE to handle service generation for lines with project or task set
        self._timesheet_service_bind_manually_set_task()
        # Call super, but ignoring global project lines with a project already set
        self = self.with_context(ignore_lines_with_project=True)
        res = super()._timesheet_service_generation()
        # Handle lines with task creation in global project, with project already set
        global_project_lines = self.with_context(
            ignore_lines_with_project=False
        )._get_so_lines_task_global_project()
        for line in global_project_lines.sorted(lambda line: (line.sequence, line.id)):
            # Create the task using the line's project
            if not line.task_id:
                line._timesheet_create_task(line.project_id)
            # If the order project is not set, use the one in the line
            if not line.order_id.project_id:
                line.order_id.project_id = line.task_id.project_id
        return res

    def _timesheet_service_bind_manually_set_task(self):
        """Bind manually set tasks to the sale line

        Project Tasks and Sale Order Lines have a O-O relation through
        the sale.order.line.task_id and project.task.sale_line_id fields.

        We must maintain this inverse relation when linking an existing task to a line.
        """
        for line in self:
            if line.service_tracking not in (
                "task_global_project",
                "task_in_project",
                "project_only",
            ):
                continue
            if not line.task_id:
                continue
            # Set the task's project if it's missing
            if (
                line.task_id.project_id
                and line.project_id
                and line.task_id.project_id != line.project_id
            ):
                raise UserError(
                    self.env._(
                        "The task %(task)s is already linked to another project "
                        "(%(project)s).",
                        task=line.task_id.name,
                        project=line.task_id.project_id.display_name,
                    )
                )
            elif not line.project_id and line.task_id.project_id:
                line.project_id = line.task_id.project_id
            elif not line.task_id.project_id:
                line.task_id.project_id = (
                    line.project_id
                    or line.product_id.project_id
                    or line.order_id.project_id
                )
            # Link the task to the sale order and sale line
            if line.task_id.sale_line_id and line.task_id.sale_line_id != line:
                raise UserError(
                    self.env._(
                        "The task %(task)s is already linked to another line "
                        "(%(order)s: %(product)s).",
                        task=line.task_id.name,
                        order=line.task_id.sale_line_id.order_id.name,
                        product=line.task_id.sale_line_id.product_id.display_name,
                    )
                )
            elif (
                line.task_id.sale_order_id
                and line.task_id.sale_order_id != line.order_id
            ):
                raise UserError(
                    self.env._(
                        "The task %(task)s is already linked to another order "
                        "(%(order)s).",
                        task=line.task_id.name,
                        order=line.task_id.sale_order_id.name,
                    )
                )
            if not line.task_id.sale_line_id:
                line.task_id.sale_line_id = line
            if not line.task_id.sale_order_id:
                line.task_id.sale_order_id = line.order_id
