# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class project_project(models.Model):
    _inherit = 'project.project'

    @api.multi
    def hours_block_tree_view(self):
        self.ensure_one()
        invoice_line_obj = self.env['account.invoice.line']
        hours_block_obj = self.env['account.hours.block']
        invoice_line_ids = invoice_line_obj.search([
            ('account_analytic_id', '=', self.analytic_account_id.id),
        ])
        invoice_lines = invoice_line_obj.browse(invoice_line_ids)
        invoice_ids = [x.invoice_id.id for x in invoice_lines]
        res_ids = hours_block_obj.search([
            ('invoice_id', 'in', invoice_ids),
        ])
        domain = False
        if res_ids:
            domain = [('id', 'in', res_ids)]
        else:
            raise UserError(_("No Hours Block for this project"))
        return {
            'name': _('Hours Blocks'),
            'domain': domain,
            'res_model': 'account.hours.block',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'limit': 80,
            'res_id': res_ids or False,
        }
