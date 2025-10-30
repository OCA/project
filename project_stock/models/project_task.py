# Copyright 2022-2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ProjectTask(models.Model):
    _name = "project.task"
    _inherit = ["project.task", "analytic.mixin"]

    scrap_ids = fields.One2many(
        comodel_name="stock.scrap", inverse_name="task_id", string="Scraps"
    )
    scrap_count = fields.Integer(
        compute="_compute_scrap_move_count", string="Scrap Move"
    )
    move_ids = fields.One2many(
        comodel_name="stock.move",
        inverse_name="raw_material_task_id",
        string="Stock Moves",
        copy=False,
        domain=[("scrapped", "=", False)],
    )
    use_stock_moves = fields.Boolean(related="stage_id.use_stock_moves")
    done_stock_moves = fields.Boolean(related="stage_id.done_stock_moves")
    stock_moves_is_locked = fields.Boolean(default=True)
    allow_moves_action_confirm = fields.Boolean(
        compute="_compute_allow_moves_action_confirm"
    )
    allow_moves_action_assign = fields.Boolean(
        compute="_compute_allow_moves_action_assign"
    )
    stock_state = fields.Selection(
        selection=[
            ("pending", "Pending"),
            ("confirmed", "Confirmed"),
            ("assigned", "Assigned"),
            ("done", "Done"),
            ("cancel", "Cancel"),
        ],
        compute="_compute_stock_state",
    )
    picking_type_id = fields.Many2one(
        comodel_name="stock.picking.type",
        string="Operation Type",
        readonly=False,
        domain="[('company_id', '=', company_id)]",
        index=True,
        check_company=True,
    )
    location_id = fields.Many2one(
        comodel_name="stock.location",
        string="Source Location",
        readonly=False,
        index=True,
        check_company=True,
    )
    location_dest_id = fields.Many2one(
        comodel_name="stock.location",
        string="Destination Location",
        readonly=False,
        index=True,
        check_company=True,
    )
    stock_analytic_date = fields.Date(string="Analytic date")
    unreserve_visible = fields.Boolean(
        string="Allowed to Unreserve Inventory",
        compute="_compute_unreserve_visible",
        help="Technical field to check when we can unreserve",
    )
    stock_analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Move Analytic Account",
        help="Move created will be assigned to this analytic account",
    )
    stock_analytic_distribution = fields.Json(
        "Analytic Distribution",
        copy=True,
        readonly=False,
    )
    stock_analytic_line_ids = fields.One2many(
        comodel_name="account.analytic.line",
        inverse_name="stock_task_id",
        string="Analytic Lines",
    )
    group_id = fields.Many2one(
        comodel_name="procurement.group",
    )

    def _compute_scrap_move_count(self):
        data = self.env["stock.scrap"].read_group(
            [("task_id", "in", self.ids)], ["task_id"], ["task_id"]
        )
        count_data = {item["task_id"][0]: item["task_id_count"] for item in data}
        for item in self:
            item.scrap_count = count_data.get(item.id, 0)

    @api.depends("move_ids", "move_ids.state")
    def _compute_allow_moves_action_confirm(self):
        for item in self:
            item.allow_moves_action_confirm = any(
                move.state == "draft" for move in item.move_ids
            )

    @api.depends("move_ids", "move_ids.state")
    def _compute_allow_moves_action_assign(self):
        for item in self:
            item.allow_moves_action_assign = any(
                move.state in ("confirmed", "partially_available")
                for move in item.move_ids
            )

    @api.depends("move_ids", "move_ids.state")
    def _compute_stock_state(self):
        for task in self:
            task.stock_state = "pending"
            if task.move_ids:
                states = task.mapped("move_ids.state")
                for state in ("confirmed", "assigned", "done", "cancel"):
                    if state in states:
                        task.stock_state = state
                        break

    @api.depends("move_ids", "move_ids.quantity_done")
    def _compute_unreserve_visible(self):
        for item in self:
            already_reserved = item.mapped("move_ids.move_line_ids")
            any_quantity_done = any([m.quantity_done > 0 for m in item.move_ids])
            item.unreserve_visible = not any_quantity_done and already_reserved

    @api.onchange("picking_type_id")
    def _onchange_picking_type_id(self):
        self.location_id = self.picking_type_id.default_location_src_id.id
        self.location_dest_id = self.picking_type_id.default_location_dest_id.id

    def _check_tasks_with_pending_moves(self):
        if self.move_ids and "assigned" in self.mapped("move_ids.state"):
            raise UserError(
                _("It is not possible to change this with reserved movements in tasks.")
            )

    def _update_moves_info(self):
        for item in self:
            item._check_tasks_with_pending_moves()
            picking_type = item.picking_type_id or item.project_id.picking_type_id
            location = item.location_id or item.project_id.location_id
            location_dest = item.location_dest_id or item.project_id.location_dest_id
            moves = item.move_ids.filtered(
                lambda x: x.state not in ("cancel", "done")
                and (x.location_id != location or x.location_dest_id != location_dest)
            )
            moves.update(
                {
                    "warehouse_id": location.warehouse_id.id,
                    "location_id": location.id,
                    "location_dest_id": location_dest.id,
                    "picking_type_id": picking_type.id,
                }
            )
        self.action_assign()

    @api.model
    def _prepare_procurement_group_vals(self):
        return {"name": "Task-ID: %s" % self.id}

    def action_confirm(self):
        self.mapped("move_ids")._action_confirm()

    def action_assign(self):
        self.action_confirm()
        self.mapped("move_ids")._action_assign()

    def button_scrap(self):
        self.ensure_one()
        move_items = self.move_ids.filtered(lambda x: x.state not in ("done", "cancel"))
        return {
            "name": _("Scrap"),
            "view_mode": "form",
            "res_model": "stock.scrap",
            "view_id": self.env.ref("stock.stock_scrap_form_view2").id,
            "type": "ir.actions.act_window",
            "context": {
                "default_task_id": self.id,
                "product_ids": move_items.mapped("product_id").ids,
                "default_company_id": self.company_id.id,
            },
            "target": "new",
        }

    def do_unreserve(self):
        for item in self:
            item.move_ids.filtered(
                lambda x: x.state not in ("done", "cancel")
            )._do_unreserve()
        return True

    def button_unreserve(self):
        self.ensure_one()
        self.do_unreserve()
        return True

    def action_cancel(self):
        """Cancel the stock moves and remove the analytic lines created from
        stock moves when cancelling the task.
        """
        for move in self.move_ids:
            move.action_cancel_from_task()
        # Use sudo to avoid error for users with no access to analytic
        # Although the action_cancel_from_task() method should have deleted
        # all analytical entries, we want to make sure there are no old records left.
        self.sudo().stock_analytic_line_ids.unlink()
        self.stock_moves_is_locked = True
        return True

    def action_toggle_stock_moves_is_locked(self):
        self.ensure_one()
        self.stock_moves_is_locked = not self.stock_moves_is_locked
        return True

    def action_done(self):
        # Filter valid stock moves (avoiding those done and cancelled).
        for move in self.mapped("move_ids").filtered(
            lambda x: x.state not in ("done", "cancel")
        ):
            move.quantity_done = move.reserved_availability
        self.move_ids._action_done()

    def action_see_move_scrap(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("stock.action_stock_scrap")
        action["domain"] = [("task_id", "=", self.id)]
        action["context"] = dict(self._context, default_origin=self.name)
        return action

    def write(self, vals):
        res = super().write(vals)
        if "stage_id" in vals:
            stage = self.env["project.task.type"].browse(vals.get("stage_id"))
            if stage.done_stock_moves:
                # Avoid permissions error if the user does not have access to stock.
                self.sudo().action_assign()
        # Update info
        field_names = ("location_id", "location_dest_id")
        if any(vals.get(field) for field in field_names):
            self._update_moves_info()
        return res

    def unlink(self):
        # Use sudo to avoid error to users with no access to analytic
        # related to hr_timesheet addon
        return super(ProjectTask, self.sudo()).unlink()


class ProjectTaskType(models.Model):
    _inherit = "project.task.type"

    use_stock_moves = fields.Boolean(
        help="If you mark this check, when a task goes to this state, "
        "it will use stock moves",
    )
    done_stock_moves = fields.Boolean(
        help="If you check this box, when a task is in this state, you will not "
        "be able to add more stock moves but they can be viewed."
    )
