# -*- coding: utf-8 -*-
###############################################################################
#
#   Module for OpenERP
#   Copyright (C) 2014 Akretion (http://www.akretion.com).
#   Copyright (C) 2010-2013 Akretion LDTA (<http://www.akretion.com>)
#   @author Sébastien BEAU <sebastien.beau@akretion.com>
#   @author Benoît GUILLOT <benoit.guillot@akretion.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp.osv import fields, orm
from datetime import date


class sale_order(orm.Model):
    _inherit = "sale.order"

    _columns = {
        'related_project_id': fields.many2one(
            'project.project',
            'Project',
            readonly=True,
            states={'draft': [('readonly', False)]}
        ),
    }

    def onchange_related_project_id(self, cr, uid, ids, related_project_id, context=None):
        project_obj = self.pool['project.project']
        if related_project_id:
            project = project_obj.browse(cr, uid, related_project_id, context=context)
            return {'value': {'project_id': project.analytic_account_id.id}}
        return {}

    def _prepare_project_vals(self, cr, uid, order, context=None):
        name = u" %s - %s - %s" % (
            order.partner_id.name,
            date.today().year,
            order.name)
        return {
            'user_id': order.user_id.id,
            'name': name,
            'partner_id': order.partner_id.id,
        }

    def action_create_project(self, cr, uid, ids, context=None):
        project_obj = self.pool['project.project']
        for order in self.browse(cr, uid, ids, context=context):
            vals = self._prepare_project_vals(cr, uid, order, context)
            project_id = project_obj.create(cr, uid, vals, context=context)
            project = project_obj.browse(cr, uid, project_id, context=context)
            order.write({
                'related_project_id': project_id,
                'project_id': project.analytic_account_id.id
            })
        return True
