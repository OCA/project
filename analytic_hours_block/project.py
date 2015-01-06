# -*- coding: utf-8 -*-
from osv import orm
from openerp.tools.translate import _


class project_project(orm.Model):
    _inherit = 'project.project'

    def hours_block_tree_view(self, cr, uid, ids, context):
        invoice_line_obj = self.pool.get('account.invoice.line')
        hours_block_obj = self.pool.get('account.hours.block')
        project = self.browse(cr, uid, ids)[0]
        invoice_line_ids = invoice_line_obj.search(
            cr, uid,
            [('account_analytic_id',
              '=',
              project.analytic_account_id.id)])
        invoice_lines = invoice_line_obj.browse(cr, uid, invoice_line_ids)
        invoice_ids = [x.invoice_id.id for x in invoice_lines]
        res_ids = hours_block_obj.search(cr, uid, [('invoice_id',
                                                    'in', invoice_ids)])
        domain = False
        if res_ids:
            domain = [('id', 'in', res_ids)]
        else:
            raise orm.except_orm(_('Warning'),
                                 _("No Hours Block for this project"))

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
