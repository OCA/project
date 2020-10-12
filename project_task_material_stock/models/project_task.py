# Copyright 2015 Tecnativa - Sergio Teruel
# Copyright 2015 Tecnativa - Carlos Dauden
# Copyright 2016-2017 Tecnativa - Vicent Cubells
# Copyright 2019 Valentin Vinagre <valentin.vinagre@qubiq.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import _, api, exceptions, fields, models


class ProjectTaskType(models.Model):
    _inherit = "project.task.type"

    consume_material = fields.Boolean(
        help="If you mark this check, when a task goes to this state, "
        "it will consume the associated materials",
    )


class Task(models.Model):
    _inherit = "project.task"

    @api.depends("material_ids.stock_move_id")
    def _compute_stock_move(self):
        for task in self:
            task.stock_move_ids = task.mapped("material_ids.stock_move_id")

    @api.depends("material_ids.analytic_line_id")
    def _compute_analytic_line(self):
        for task in self:
            task.analytic_line_ids = task.mapped("material_ids.analytic_line_id")

    @api.depends("stock_move_ids.state")
    def _compute_stock_state(self):
        for task in self:
            if not task.stock_move_ids:
                task.stock_state = "pending"
            else:
                states = task.mapped("stock_move_ids.state")
                for state in ("confirmed", "assigned", "done"):
                    if state in states:
                        task.stock_state = state
                        break

    picking_id = fields.Many2one("stock.picking", related="stock_move_ids.picking_id",)
    stock_move_ids = fields.Many2many(
        comodel_name="stock.move",
        compute="_compute_stock_move",
        string="Stock Moves",
        store=True,
    )
    analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Move Analytic Account",
        help="Move created will be assigned to this analytic account",
    )
    analytic_line_ids = fields.Many2many(
        comodel_name="account.analytic.line",
        compute="_compute_analytic_line",
        string="Analytic Lines",
    )
    consume_material = fields.Boolean(related="stage_id.consume_material",)
    stock_state = fields.Selection(
        selection=[
            ("pending", "Pending"),
            ("confirmed", "Confirmed"),
            ("assigned", "Assigned"),
            ("done", "Done"),
        ],
        compute="_compute_stock_state",
    )
    location_source_id = fields.Many2one(
        comodel_name="stock.location",
        string="Source Location",
        index=True,
        help="Keep this field empty to use the default value from the project.",
    )
    location_dest_id = fields.Many2one(
        comodel_name="stock.location",
        string="Destination Location",
        index=True,
        help="Keep this field empty to use the default value from the project.",
    )

    def unlink_stock_move(self):
        res = False
        moves = self.mapped("stock_move_ids")
        moves_done = moves.filtered(lambda r: r.state == "done")
        if not moves_done:
            moves.filtered(lambda r: r.state == "assigned")._do_unreserve()
            moves.filtered(
                lambda r: r.state in {"waiting", "confirmed", "assigned"}
            ).write({"state": "draft"})
            res = moves.unlink()
        return res

    def write(self, vals):
        res = super(Task, self).write(vals)
        for task in self:
            if "stage_id" in vals or "material_ids" in vals:
                if task.consume_material:
                    todo_lines = task.material_ids.filtered(
                        lambda m: not m.stock_move_id
                    )
                    if todo_lines:
                        todo_lines.create_stock_move()
                        todo_lines.create_analytic_line()
                else:
                    if task.unlink_stock_move() and task.material_ids.mapped(
                        "analytic_line_id"
                    ):
                        raise exceptions.Warning(
                            _(
                                "You can't move to a not consume stage if "
                                "there are already analytic lines"
                            )
                        )
                    task.material_ids.mapped("analytic_line_id").unlink()
        return res

    def unlink(self):
        self.mapped("stock_move_ids").unlink()
        self.mapped("analytic_line_ids").unlink()
        return super(Task, self).unlink()

    def action_assign(self):
        self.mapped("stock_move_ids")._action_assign()

    def action_done(self):
        for move in self.mapped("stock_move_ids"):
            move.quantity_done = move.product_uom_qty
        self.mapped("stock_move_ids")._action_done()


class ProjectTaskMaterial(models.Model):
    _inherit = "project.task.material"

    stock_move_id = fields.Many2one(comodel_name="stock.move", string="Stock Move",)
    analytic_line_id = fields.Many2one(
        comodel_name="account.analytic.line", string="Analytic Line",
    )
    product_uom_id = fields.Many2one(comodel_name="uom.uom", string="Unit of Measure")
    product_id = fields.Many2one(domain="[('type', 'in', ('consu', 'product'))]")

    @api.onchange("product_id")
    def _onchange_product_id(self):
        self.product_uom_id = self.product_id.uom_id.id
        return {
            "domain": {
                "product_uom_id": [
                    ("category_id", "=", self.product_id.uom_id.category_id.id)
                ]
            }
        }

    def _prepare_stock_move(self):
        product = self.product_id
        res = {
            "product_id": product.id,
            "name": product.partner_ref,
            "state": "confirmed",
            "product_uom": self.product_uom_id.id or product.uom_id.id,
            "product_uom_qty": self.quantity,
            "origin": self.task_id.name,
            "location_id": self.task_id.location_source_id.id
            or self.task_id.project_id.location_source_id.id
            or self.env.ref("stock.stock_location_stock").id,
            "location_dest_id": self.task_id.location_dest_id.id
            or self.task_id.project_id.location_dest_id.id
            or self.env.ref("stock.stock_location_customers").id,
        }
        return res

    def create_stock_move(self):
        pick_type = self.env.ref(
            "project_task_material_stock.project_task_material_picking_type"
        )
        task = self[0].task_id
        picking_id = task.picking_id or self.env["stock.picking"].create(
            {
                "origin": "{}/{}".format(task.project_id.name, task.name),
                "partner_id": task.partner_id.id,
                "picking_type_id": pick_type.id,
                "location_id": pick_type.default_location_src_id.id,
                "location_dest_id": pick_type.default_location_dest_id.id,
            }
        )
        for line in self:
            if not line.stock_move_id:
                move_vals = line._prepare_stock_move()
                move_vals.update({"picking_id": picking_id.id or False})
                move_id = self.env["stock.move"].create(move_vals)
                line.stock_move_id = move_id.id

    def _prepare_analytic_line(self):
        product = self.product_id
        company_id = self.env.company
        analytic_account = getattr(
            self.task_id, "analytic_account_id", False
        ) or getattr(self.task_id.project_id, "analytic_account_id", False)
        if not analytic_account:
            raise exceptions.Warning(
                _("You must assign an analytic account for this task/project.")
            )
        res = {
            "name": self.task_id.name + ": " + product.name,
            "ref": self.task_id.name,
            "product_id": product.id,
            "unit_amount": self.quantity,
            "account_id": analytic_account.id,
            "user_id": self._uid,
            "product_uom_id": self.product_uom_id.id,
            "company_id": analytic_account.company_id.id or self.env.user.company_id.id,
            "partner_id": self.task_id.partner_id.id
            or self.task_id.project_id.partner_id.id
            or None,
            "task_material_id": [(6, 0, [self.id])],
        }
        amount_unit = self.product_id.with_context(
            uom=self.product_uom_id.id
        ).price_compute("standard_price")[self.product_id.id]
        amount = amount_unit * self.quantity or 0.0
        result = round(amount, company_id.currency_id.decimal_places) * -1
        vals = {"amount": result}
        if "employee_id" in self.env["account.analytic.line"]._fields:
            vals["employee_id"] = (
                self.env["hr.employee"]
                .search([("user_id", "=", self.task_id.user_id.id)], limit=1)
                .id
            )
        res.update(vals)
        return res

    def create_analytic_line(self):
        for line in self:
            self.env["account.analytic.line"].create(line._prepare_analytic_line())

    def unlink_stock_move(self):
        if not self.stock_move_id.state == "done":
            if self.stock_move_id.state == "assigned":
                self.stock_move_id._do_unreserve()
            if self.stock_move_id.state in ("waiting", "confirmed", "assigned"):
                self.stock_move_id.write({"state": "draft"})
            picking_id = self.stock_move_id.picking_id
            self.stock_move_id.unlink()
            if (
                not picking_id.move_line_ids_without_package
                and picking_id.state == "draft"
            ):
                picking_id.unlink()

    def _update_unit_amount(self):
        # The analytical amount is updated with the value of the
        # stock movement, because if the product has a tracking by
        # lot / serial number, the cost when creating the
        # analytical line is not correct.
        for sel in self.filtered(
            lambda x: x.stock_move_id.state == "done"
            and x.analytic_line_id.amount != x.stock_move_id.product_id.standard_price
        ):
            sel.analytic_line_id.amount = sel.stock_move_id.product_id.standard_price

    def unlink(self):
        self.unlink_stock_move()
        if self.stock_move_id:
            raise exceptions.Warning(
                _(
                    "You can't delete a consumed material if already "
                    "have stock movements done."
                )
            )
        self.analytic_line_id.unlink()
        return super(ProjectTaskMaterial, self).unlink()
