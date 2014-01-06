# -*- coding: utf-8 -*-
###############################################################################
#                                                                             #
#   sale_project for OpenERP                                                  #
#   Copyright (C) 2013 Akretion Benoît GUILLOT <benoit.guillot@akretion.com>  #
#                                                                             #
#   This program is free software: you can redistribute it and/or modify      #
#   it under the terms of the GNU Affero General Public License as            #
#   published by the Free Software Foundation, either version 3 of the        #
#   License, or (at your option) any later version.                           #
#                                                                             #
#   This program is distributed in the hope that it will be useful,           #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
#   GNU Affero General Public License for more details.                       #
#                                                                             #
#   You should have received a copy of the GNU Affero General Public License  #
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.     #
#                                                                             #
###############################################################################

from openerp.osv import fields, orm, osv
from openerp.osv.osv import except_osv
from tools.translate import _


class sale_order(orm.Model):
    _inherit = "sale.order"

    _columns = {
        'true_project_id': fields.many2one('project.project', 'Project',
                                           readonly=True,
                                           states={'draft': [('readonly', False)]}
                                           ),
    }

    def true_project_id_change(self, cr, uid, ids, true_project_id):
        project_obj = self.pool['project.project']
        res = {}
        if true_project_id:
            project_id = project_obj.browse(cr, uid, true_project_id).analytic_account_id.id
            res = {'value': {'project_id': project_id}}
        return res

    def create_project(self, cr, uid, ids, context=None):
        project_obj = self.pool['project.project']
        if context is None:
            context = {}
        for order in self.browse(cr, uid, ids, context=context):
            context['partner_id'] = order.partner_id.id
            context['order_name'] = order.name
            project_vals = project_obj.default_get(cr, uid,
                                                   ['name', 'partner_id'],
                                                   context=context)
            if order.user_id:
                project_vals['user_id'] = order.user_id.id
            project_id = project_obj.create(cr, uid, project_vals, context=context)
            analytic_account_id = project_obj.browse(cr, uid,
                                                     project_id,
                                                     context=context).analytic_account_id.id
            order.write({
                'true_project_id': project_id,
                'project_id': analytic_account_id,
            })
        return True

    def _prepare_write_vals(self, cr, uid, order, line, context=None):
        return {
            'project_id': order.true_project_id.id,
            'qty': line.product_uom_qty,
            'state': 'confirmed',
        }

    def action_button_confirm(self, cr, uid, ids, context=None):
        for order in self.browse(cr, uid, ids, context=context):
            if order.true_project_id:
                feature_ids = []
                for line in order.order_line:
                    if line.feature_id:
                        write_vals = self._prepare_write_vals(
                            cr, uid, order, line, context=context)
                        line.feature_id.write(write_vals, context=context)
        return super(sale_order, self).action_button_confirm(cr, uid, ids, context=context)

    def action_ship_create(self, cr, uid, ids, context=None):
        for order in self.browse(cr, uid, ids, context=context):
            if not order.true_project_id:
                self._create_pickings_and_procurements(cr, uid, order, order.order_line, None, context=context)
        return True
