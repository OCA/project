# Copyright 2015 Tecnativa - Sergio Teruel
# Copyright 2015 Tecnativa - Carlos Dauden
# Copyright 2016-2017 Tecnativa - Vicent Cubells
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import _, api, exceptions, fields, models


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    consume_material = fields.Boolean(
        help="If you mark this check, when a task goes to this state, "
             "it will consume the associated materials",
    )


class Task(models.Model):
    _inherit = "project.task"

    @api.multi
    @api.depends('material_ids.stock_move_id')
    def _compute_stock_move(self):
        for task in self:
            task.stock_move_ids = task.mapped('material_ids.stock_move_id')

    @api.multi
    @api.depends('material_ids.analytic_line_id')
    def _compute_analytic_line(self):
        for task in self:
            task.analytic_line_ids = task.mapped(
                'material_ids.analytic_line_id')

    @api.multi
    @api.depends('stock_move_ids.state')
    def _compute_stock_state(self):
        for task in self:
            if not task.stock_move_ids:
                task.stock_state = 'pending'
            else:
                states = task.mapped("stock_move_ids.state")
                for state in ("confirmed", "assigned", "done"):
                    if state in states:
                        task.stock_state = state
                        break

    picking_id = fields.Many2one("stock.picking",
                                 related="stock_move_ids.picking_id")
    stock_move_ids = fields.Many2many(
        comodel_name='stock.move',
        compute='_compute_stock_move',
        string='Stock Moves',
    )
    analytic_account_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Analytic Account',
        help='Move created will be assigned to this analytic account',
    )
    analytic_line_ids = fields.Many2many(
        comodel_name='account.analytic.line',
        compute='_compute_analytic_line',
        string='Analytic Lines',
    )
    consume_material = fields.Boolean(
        related='stage_id.consume_material',
    )
    stock_state = fields.Selection(
        selection=[
            ('pending', 'Pending'),
            ('confirmed', 'Confirmed'),
            ('assigned', 'Assigned'),
            ('done', 'Done')],
        compute='_compute_stock_state',
    )
    location_source_id = fields.Many2one(
        comodel_name='stock.location',
        string='Source Location',
        index=True,
        help='Default location from which materials are consumed.',
    )
    location_dest_id = fields.Many2one(
        comodel_name='stock.location',
        string='Destination Location',
        index=True,
        help='Default location to which materials are consumed.',
    )

    @api.multi
    def unlink_stock_move(self):
        res = False
        moves = self.mapped('stock_move_ids')
        moves_done = moves.filtered(lambda r: r.state == 'done')
        if not moves_done:
            moves.filtered(lambda r: r.state == 'assigned')._do_unreserve()
            moves.filtered(
                lambda r: r.state in {'waiting', 'confirmed', 'assigned'}
            ).write({'state': 'draft'})
            res = moves.unlink()
        return res

    @api.multi
    def write(self, vals):
        res = super(Task, self).write(vals)
        for task in self:
            if 'stage_id' in vals or 'material_ids' in vals:
                if task.stage_id.consume_material:
                    todo_lines = task.material_ids.filtered(
                        lambda m: not m.stock_move_id
                    )
                    if todo_lines:
                        todo_lines.create_stock_move()
                        todo_lines.create_analytic_line()

                else:
                    if task.unlink_stock_move():
                        if task.material_ids.mapped(
                                'analytic_line_id'):
                            raise exceptions.Warning(
                                _("You can't move to a not consume stage if "
                                  "there are already analytic lines")
                            )
                    task.material_ids.mapped('analytic_line_id').unlink()
        return res

    @api.multi
    def unlink(self):
        self.mapped('stock_move_ids').unlink()
        self.mapped('analytic_line_ids').unlink()
        return super(Task, self).unlink()

    @api.multi
    def action_assign(self):
        self.mapped('stock_move_ids')._action_assign()

    @api.multi
    def action_done(self):
        for move in self.mapped('stock_move_ids'):
            move.quantity_done = move.product_uom_qty
        self.mapped('stock_move_ids')._action_done()


class ProjectTaskMaterial(models.Model):
    _inherit = "project.task.material"

    stock_move_id = fields.Many2one(
        comodel_name='stock.move',
        string='Stock Move',
    )
    analytic_line_id = fields.Many2one(
        comodel_name='account.analytic.line',
        string='Analytic Line',
    )
    product_uom_id = fields.Many2one(
        comodel_name='product.uom',
        oldname="product_uom",
        string='Unit of Measure',
    )

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.product_uom_id = self.product_id.uom_id.id
        return {'domain': {'product_uom_id': [
            ('category_id', '=', self.product_id.uom_id.category_id.id)]}}

    def _prepare_stock_move(self):
        product = self.product_id
        res = {
            'product_id': product.id,
            'name': product.partner_ref,
            'state': 'confirmed',
            'product_uom': self.product_uom_id.id or product.uom_id.id,
            'product_uom_qty': self.quantity,
            'origin': self.task_id.name,
            'location_id':
                self.task_id.location_source_id.id or
                self.task_id.project_id.location_source_id.id or
                self.env.ref('stock.stock_location_stock').id,
            'location_dest_id':
                self.task_id.location_dest_id.id or
                self.task_id.project_id.location_dest_id.id or
                self.env.ref('stock.stock_location_customers').id,
        }
        return res

    @api.multi
    def create_stock_move(self):
        pick_type = self.env.ref(
            'project_task_material_stock.project_task_material_picking_type')

        task = self[0].task_id
        picking_id = task.picking_id or self.env['stock.picking'].create({
            'origin': "{}/{}".format(task.project_id.name, task.name),
            'partner_id': task.partner_id.id,
            'picking_type_id': pick_type.id,
            'location_id': pick_type.default_location_src_id.id,
            'location_dest_id': pick_type.default_location_dest_id.id,
        })

        for line in self:
            if not line.stock_move_id:
                move_vals = line._prepare_stock_move()
                move_vals.update({'picking_id': picking_id.id or False})
                move_id = self.env['stock.move'].create(move_vals)
                line.stock_move_id = move_id.id

    def _prepare_analytic_line(self):
        product = self.product_id
        company_id = self.env['res.company']._company_default_get(
            'account.analytic.line')
        analytic_account = getattr(self.task_id, 'analytic_account_id', False)\
            or self.task_id.project_id.analytic_account_id
        res = {
            'name': self.task_id.name + ': ' + product.name,
            'ref': self.task_id.name,
            'product_id': product.id,
            'unit_amount': self.quantity,
            'account_id': analytic_account.id,
            'user_id': self._uid,
            'product_uom_id': self.product_uom_id.id,
        }
        amount_unit = \
            self.product_id.with_context(uom=self.product_uom_id.id).price_get(
                'standard_price')[self.product_id.id]
        amount = amount_unit * self.quantity or 0.0
        result = round(amount, company_id.currency_id.decimal_places) * -1
        res.update({'amount': result})
        return res

    @api.multi
    def create_analytic_line(self):
        for line in self:
            move_id = self.env['account.analytic.line'].create(
                line._prepare_analytic_line())
            line.analytic_line_id = move_id.id
