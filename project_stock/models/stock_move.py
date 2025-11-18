# Copyright 2022-2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import api, fields, models
from odoo.tools import float_is_zero


class StockMove(models.Model):
    _inherit = "stock.move"

    task_id = fields.Many2one(
        comodel_name="project.task",
        string="Related Task",
        check_company=True,
    )
    raw_material_task_id = fields.Many2one(
        comodel_name="project.task", string="Task for material", check_company=True
    )
    analytic_line_ids = fields.One2many(
        comodel_name="account.analytic.line",
        inverse_name="stock_move_id",
        string="Analytic Lines",
    )
    show_cancel_button_in_task = fields.Boolean(
        compute="_compute_show_cancel_button_in_task"
    )

    @api.onchange("product_id")
    def _onchange_product_id(self):
        """It is necessary to overwrite the name to prevent set product name
        from being auto-defined."""
        res = super()._onchange_product_id()
        if self.raw_material_task_id:
            self.name = self.raw_material_task_id.name
        return res

    def _compute_show_cancel_button_in_task(self):
        dp = self.env["decimal.precision"].precision_get("Product Unit of Measure")
        for item in self:
            item.show_cancel_button_in_task = bool(
                item.raw_material_task_id
                and item.raw_material_task_id.stock_moves_is_locked
                and item.raw_material_task_id.done_stock_moves
                and item.state not in ("draft", "cancel")
                and (
                    (
                        item.state == "done"
                        and not float_is_zero(item.quantity_done, precision_digits=dp)
                    )
                    or (
                        item.state != "done"
                        and not float_is_zero(item.product_uom_qty, precision_digits=dp)
                    )
                )
            )

    def action_cancel_from_task(self):
        self.ensure_one()
        if not self.show_cancel_button_in_task:
            return
        # Use sudo to avoid error for users with no access to analytic
        analytic_lines = self.sudo().analytic_line_ids
        task_analytic_lines = self.raw_material_task_id.sudo().stock_analytic_line_ids
        if analytic_lines:
            analytic_lines.unlink()
        elif not analytic_lines and task_analytic_lines and self.state == "done":
            # Previously, analytic lines were not linked to the stock_move_id field,
            # so we have to deduce which ones were linked.
            data = self._prepare_analytic_line_from_task()
            if data:
                # Depending on whether the account module is installed or not, it will
                # be filtered by one field or another.
                f_name = "product_id" if "product_id" in data else "name"
                f_value = data[f_name]
                if f_name == "product_id":
                    f_value = self.env["product.product"].browse(f_value)
                analytic_lines = task_analytic_lines.filtered(
                    lambda x: x.unit_amount == data["unit_amount"]
                    and x[f_name] == f_value
                )
                analytic_lines.unlink()
        # It is important to do this process at the end, so that if
        # the _prepare_analytic_line_from_task() method is used, it has the correct
        # value.
        if self.state == "done":
            self.move_line_ids.write({"qty_done": 0})
        else:
            self._action_cancel()

    def _prepare_analytic_line_from_task(self):
        product = self.product_id
        company_id = self.env.company
        task = self.task_id or self.raw_material_task_id
        analytic_account = (
            task.stock_analytic_account_id or task.project_id.analytic_account_id
        )
        if not analytic_account:
            return False
        # Apply sudo() in case there is any rule that does not allow access to
        # the analytic account, for example with analytic_hr_department_restriction
        analytic_account = analytic_account.sudo()
        res = {
            "date": (
                task.stock_analytic_date
                or task.project_id.stock_analytic_date
                or fields.date.today()
            ),
            "name": task.name + ": " + product.name,
            "unit_amount": self.quantity_done,
            "account_id": analytic_account.id,
            "user_id": self._uid,
            "product_uom_id": self.product_uom.id,
            "company_id": analytic_account.company_id.id or self.env.company.id,
            "partner_id": task.partner_id.id or task.project_id.partner_id.id or False,
            "stock_move_id": self.id,
            "stock_task_id": task.id,
        }
        amount_unit = product.with_context(uom=self.product_uom.id).price_compute(
            "standard_price"
        )[product.id]
        amount = amount_unit * self.quantity_done or 0.0
        result = round(amount, company_id.currency_id.decimal_places) * -1
        vals = {"amount": result}
        analytic_line_fields = self.env["account.analytic.line"]._fields
        # Extra fields added in account addon
        if "ref" in analytic_line_fields:
            vals["ref"] = task.name
        if "product_id" in analytic_line_fields:
            vals["product_id"] = product.id
        # Prevent incoherence when hr_timesheet addon is installed.
        if "project_id" in analytic_line_fields:
            vals["project_id"] = False
        # distributions
        if task.stock_analytic_distribution:
            new_amount = 0
            for distribution in task.stock_analytic_distribution.values():
                new_amount -= (amount / 100) * distribution
            vals["amount"] = new_amount
        res.update(vals)
        return res

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        if self.env.context.get("default_raw_material_task_id"):
            task = self.env["project.task"].browse(
                self.env.context.get("default_raw_material_task_id")
            )
            if not task.group_id:
                task.group_id = self.env["procurement.group"].create(
                    task._prepare_procurement_group_vals()
                )
            defaults.update(
                {
                    "group_id": task.group_id.id,
                    "location_id": (
                        task.location_id.id or task.project_id.location_id.id
                    ),
                    "location_dest_id": (
                        task.location_dest_id.id or task.project_id.location_dest_id.id
                    ),
                    "picking_type_id": (
                        task.picking_type_id.id or task.project_id.picking_type_id.id
                    ),
                }
            )
        return defaults

    def _action_done(self, cancel_backorder=False):
        """Create the analytical notes for stock movements linked to tasks."""
        moves_todo = super()._action_done(cancel_backorder)
        # Use sudo to avoid error for users with no access to analytic
        analytic_line_model = self.env["account.analytic.line"].sudo()
        for move in moves_todo.filtered(lambda x: x.raw_material_task_id):
            vals = move._prepare_analytic_line_from_task()
            if vals:
                analytic_line_model.create(vals)
        return moves_todo

    def action_task_product_forecast_report(self):
        self.ensure_one()
        action = self.product_id.action_product_forecast_report()
        action["context"] = {
            "active_id": self.product_id.id,
            "active_model": "product.product",
            "move_to_match_ids": self.ids,
        }
        warehouse = self.warehouse_id
        if warehouse:
            action["context"]["warehouse"] = warehouse.id
        return action


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    task_id = fields.Many2one(
        comodel_name="project.task",
        string="Task",
        compute="_compute_task_id",
        store=True,
    )

    @api.depends("move_id.raw_material_task_id", "move_id.task_id")
    def _compute_task_id(self):
        for item in self:
            task = (
                item.move_id.raw_material_task_id
                if item.move_id.raw_material_task_id
                else item.move_id.task_id
            )
            item.task_id = task if task else False
