# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Yannick Buron. Copyright Yannick Buron
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, orm


class ProjectTask(orm.Model):

    """
    Add assignment fields in project.task and recompute
    assigned partner when we change stage
    """

    _name = 'project.task'
    _inherit = ['project.task', 'project.assigned.partner.model']

    _columns = {
        'assigned_partner_id': fields.many2one('res.partner', 'Assigned to'),
        'reviewer_partner_id': fields.many2one('res.partner', 'Reviewer'),
    }

    def _get_external_config(self, cr, uid, record, context=None):
        # Get configuration from project
        res = {}
        if record.project_id:
            for config in record.project_id.assigned_partner_config_result_ids:
                res[config.stage_id.id] = self._prepare_config(
                    cr, uid, record.id, config, vals={}, context=context
                )
        return res

    def _update_assigned_partner(self, cr, uid, ids, vals, context=None):
        # Update partner either from argument or from configuration
        if 'user_id' in vals:
            vals['assigned_partner_id'] = self.pool.get('res.users').browse(
                cr, uid, vals['user_id'], context=context
            ).partner_id.id
        if 'reviewer_id' in vals:
            vals['reviewer_partner_id'] = self.pool.get('res.users').browse(
                cr, uid, vals['reviewer_id'], context=context
            ).partner_id.id

        if 'stage_id' in vals and 'assigned_partner_id' not in vals:
            for task in self.browse(cr, uid, ids, context=context):
                for config in task.assigned_partner_config_result_ids:
                    if config.stage_id.id == vals['stage_id']:
                        vals['assigned_partner_id'] = config.partner_id.id

        if 'assigned_partner_id' in vals:
            partner = self.pool.get('res.partner').browse(
                cr, uid, vals['assigned_partner_id'], context=context
            )
            if partner.user_ids:
                vals['user_id'] = partner.user_ids[0].id
            else:
                vals['user_id'] = False
        if 'reviewer_partner_id' in vals:
            partner = self.pool.get('res.partner').browse(
                cr, uid, vals['reviewer_partner_id'], context=context
            )
            if partner.user_ids:
                vals['reviewer_id'] = partner.user_ids[0].id
            else:
                vals['reviewer_id'] = False

        return vals

    def create(self, cr, uid, vals, context=None):
        # Force write function to be called on create
        res = super(ProjectTask, self).create(cr, uid, vals, context=context)
        self.write(cr, uid, [res], vals, context=context)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        # Trigger the function to update the assigned partner on write
        vals = self._update_assigned_partner(
            cr, uid, ids, vals, context=context
        )
        res = super(ProjectTask, self).write(
            cr, uid, ids, vals, context=context
        )
        return res
