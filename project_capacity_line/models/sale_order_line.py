# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


TRIGGER_FIELDS = {
    "state",
    "product_uom_qty",
    "capacity_date_start",
    "capacity_date_end",
    "product_id",
    "name",
}


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    capacity_date_start = fields.Date()
    capacity_date_end = fields.Date()

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines._update_capacity_lines()
        return lines

    def _update_capacity_lines(self):
        capacity_vals = []
        CapacityLine = self.env["capacity.line"].sudo()
        # XXX try to be smarter and only unlink those needing unlinking, update the others
        CapacityLine.search(
            [("res_id", "in", self.ids), ("res_model", "=", self._name)]
        ).unlink()
        for line in self:
            if not line.product_id.capacity_role_id:
                continue
            elif line.state in ("cancel", "sale"):
                # no capacity line for confirmed sales -> this is handled by projects and tasks
                continue
            elif not (line.capacity_date_end and line.capacity_date_start):
                _logger.info(
                    "sale line with capacity product but no dates -> ignoring %s",
                    line.id,
                )
                continue
            else:
                capacity_type = "forecast"
            uom = line.product_uom
            quantity_hours = uom._compute_quantity(
                line.product_uom_qty, self.env.ref("uom.product_uom_hour")
            )
            # import pdb; pdb.set_trace()
            capacity_vals += CapacityLine.prepare_capacity_lines(
                name=line.name,
                date_from=line.capacity_date_start,
                date_to=line.capacity_date_end,
                capacity_type=capacity_type,
                capacity_hours=-1 * quantity_hours,
                unit_cost=line.product_id.standard_price,  # XXX currency + unit conversion
                capacity_role_id=line.product_id.capacity_role_id.id,
                sale_line_id=line.id,
                project_id=line.project_id.id,
                res_model="sale.order.line",
                res_id=line.id,
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
                    ("capacity_date_end", ">=", today),
                    ("company_id", "=", company.id),
                ]
            )
            to_update._update_capacity_lines()

    def write(self, values):
        res = super().write(values)
        written_fields = set(values.keys())
        if written_fields & TRIGGER_FIELDS:
            self._update_capacity_lines()
        return res

    @api.onchange("product_id")
    def product_id_change(self):
        res = super().product_id_change()
        for line in self:
            if not line.product_id.capacity_role_id:
                line.capacity_date_start = False
                line.capacity_date_end = False
            else:
                if (
                    not line.capacity_date_start
                    and line.order_id.default_capacity_date_start
                ):
                    line.capacity_date_start = line.order_id.default_capacity_date_start
                if (
                    not line.capacity_date_end
                    and line.order_id.default_capacity_date_end
                ):
                    line.capacity_date_end = line.order_id.default_capacity_date_end
        return res

    def _timesheet_create_task_prepare_values(self, project):
        values = super()._timesheet_create_task_prepare_values(project)
        values.update(
            {
                "capacity_role_id": self.product_id.capacity_role_id.id,
                "capacity_date_planned_end": self.capacity_date_end,
                "capacity_date_planned_start": self.capacity_date_start,
            }
        )
        return values

    def _timesheet_create_project(self):
        project = super()._timesheet_create_project()
        if self.product_id.project_template_id and self.product_id.capacity_role_id:
            project.tasks.write(
                {
                    "capacity_role_id": self.product_id.capacity_role_id.id,
                    "date_end": self.capacity_date_end,
                    "date_planned_start": self.capacity_date_start,
                }
            )
        return project
