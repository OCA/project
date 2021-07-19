# Copyright 2021 Apulia Software - Nicola Malcontenti
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import _, api, exceptions, fields, models


class Task(models.Model):
    _inherit = "project.task"

    material_ids = fields.One2many(
        comodel_name="project.task.material",
        inverse_name="task_id",
        string="Material Used",
        copy=True
    )

    @api.onchange("project_id")
    def on_change_is_template(self):
        if self.project_id.analytic_account_id:
            self.analytic_account_id = self.project_id.analytic_account_id

    def action_view_pickings(self):
        self.ensure_one()
        list_of_picking = []
        for move in self.stock_move_ids:
            if move.picking_id.id in list_of_picking:
                continue
            else:
                list_of_picking.append(move.id)
        tree_id = self.env.ref('stock.vpicktree').id
        form_id = self.env.ref('stock.view_picking_form').id
        return {
            'name': 'Picking',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(tree_id,'tree'),(form_id, 'form')],
            'res_model': 'stock.picking',
            'domain': [('id', 'in', list_of_picking)]
        }
