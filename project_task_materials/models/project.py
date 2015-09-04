# -*- coding: utf-8 -*-
# (c) 2012 - 2013 Daniel Reis
# (c) 2015 Antiun Ingeniería S.L. - Sergio Teruel
# (c) 2015 Antiun Ingeniería S.L. - Carlos Dauden
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api
from openerp.tools.float_utils import float_round


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    consume_material = fields.Boolean(
        string='Consume Material',
        help="""If you select this option, when a task is in this state
        consumes materials associated""")


class Task(models.Model):
    _inherit = "project.task"

    def _get_stock_move(self):
        move_ids = [line.stock_move_id.id for line in self.material_ids
                    if line.stock_move_id]
        self.stock_move_ids = self.env['stock.move'].browse(move_ids)

    def _get_analytic_line(self):
        line_ids = [line.analytic_line_id.id for line in self.material_ids
                    if line.analytic_line_id]
        self.analytic_line_ids = \
            self.env['account.analytic.line'].browse(line_ids)

    @api.depends('stock_move_ids.state')
    def _check_stock_state(self):
        if not self.stock_move_ids:
            self.stock_state = 'pending'
        elif self.stock_move_ids.filtered(lambda r: r.state == 'confirmed'):
            self.stock_state = 'confirmed'
        elif self.stock_move_ids.filtered(lambda r: r.state == 'assigned'):
            self.stock_state = 'assigned'
        elif self.stock_move_ids.filtered(lambda r: r.state == 'done'):
            self.stock_state = 'done'

    material_ids = fields.One2many(
        comodel_name='project.task.materials', inverse_name='task_id',
        string='Materials used')
    stock_move_ids = fields.One2many(
        comodel_name='stock.move', compute='_get_stock_move',
        string='Stock Moves')
    analytic_line_ids = fields.One2many(
        comodel_name='account.analytic.line', compute='_get_analytic_line',
        string='Analytic Lines')
    consume_material = fields.Boolean(related='stage_id.consume_material')
    stock_state = fields.Selection(
        [('pending', 'Pending'),
         ('confirmed', 'Confirmed'),
         ('assigned', 'Assigned'),
         ('done', 'Done')], compute='_check_stock_state', string='Stock State')

    @api.one
    def unlink_stock_move(self):
        for move in self.stock_move_ids:
            if move.state == 'assigned':
                move.do_unreserve()
            if move.state in ['waiting', 'confirmed', 'assigned']:
                move.state = 'draft'
            move.unlink()

    @api.one
    def write(self, vals):
        res = super(Task, self).write(vals)
        if 'stage_id' in vals:
            if self.consume_material:
                self.material_ids.create_stock_move()
                self.material_ids.create_analytic_line()
            else:
                self.unlink_stock_move()
                self.analytic_line_ids.unlink()
        return res

    @api.multi
    def action_assign(self):
        self.stock_move_ids.action_assign()

    @api.multi
    def action_done(self):
        self.stock_move_ids.action_done()
        pass


class ProjectTaskMaterials(models.Model):
    _name = "project.task.materials"
    _description = "Task Materials Used"
    task_id = fields.Many2one(
        comodel_name='project.task', string='Task', ondelete='cascade',
        required=True)
    product_id = fields.Many2one(
        comodel_name='product.product', string='Product', required=True)
    quantity = fields.Float(string='Quantity')
    stock_move_id = fields.Many2one(
        comodel_name='stock.move', string='Stock Move')
    analytic_line_id = fields.Many2one(
        comodel_name='account.analytic.line', string='Analytic Line')

    def _prepare_stock_move(self):
        product = self.product_id
        res = {
            'product_id': product.id,
            'name': product.partner_ref,
            'state': 'confirmed',
            'product_uom': product.uom_id.id,
            'product_uos': product.uos_id and product.uos_id.id or False,
            'product_uom_qty': self.quantity,
            'product_uos_qty': self.quantity,
            'origin': self.task_id.name,
            'location_id':
            product.product_tmpl_id.property_stock_procurement.id,
            'location_dest_id': self.env.ref(
                'stock.stock_location_customers').id,
        }
        if product.uos_id and product.uom_id and \
                (product.uos_id != product.uom_id):
            precision = self.env['decimal.precision'].precision_get(
                'Product UoS')
            res['product_uos_qty'] = float_round(
                self.quantity * product.uos_coeff, precision_digits=precision)
        return res

    @api.one
    def create_stock_move(self):
        move_id = self.env['stock.move'].create(self._prepare_stock_move())
        self.stock_move_id = move_id.id

    def _prepare_analytic_line(self):
        product = self.product_id
        company_id = self.env['res.company']._company_default_get(
            'account.analytic.line')
        journal = self.env.ref(
            'project_task_materials.analytic_journal_sale_materials')
        res = {
            'name': self.task_id.name + ': ' + product.name,
            'ref': self.task_id.name,
            'product_id': product.id,
            'journal_id': journal.id,
            'unit_amount': self.quantity,
            'account_id': self.task_id.project_id.analytic_account_id.id,
            'to_invoice':
            self.task_id.project_id.analytic_account_id.to_invoice.id,
            'user_id': self._uid,
        }
        analytic_line_obj = self.pool.get('account.analytic.line')
        amount_dic = analytic_line_obj.on_change_unit_amount(
            self._cr, self._uid, self._ids, product.id, self.quantity,
            company_id, False, journal.id, self._context)
        res.update(amount_dic['value'])
        return res

    @api.one
    def create_analytic_line(self):
        move_id = self.env['account.analytic.line'].create(
            self._prepare_analytic_line())
        self.analytic_line_id = move_id.id
