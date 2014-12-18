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


class ProjectAssignedPartnerModel(orm.AbstractModel):

    """
    Abstract class used by project and task to create config lines.
    Inherit base.config.inherit.model.
    """

    _name = 'project.assigned.partner.model'
    _inherit = ['base.config.inherit.model']

    _base_config_inherit_model = 'project.assigned.partner.config'
    _base_config_inherit_key = 'stage_id'
    _base_config_inherit_o2m = 'assigned_partner_config_ids'

    _columns = {
        'assigned_partner_config_ids': fields.one2many(
            'project.assigned.partner.config', 'res_id',
            domain=lambda self: [
                ('model', '=', self._name), ('stored', '=', False)
            ],
            auto_join=True,
            string='Assigned Partner configuration'
        ),
        'assigned_partner_config_result_ids': fields.one2many(
            'project.assigned.partner.config', 'res_id',
            domain=lambda self: [
                ('model', '=', self._name), ('stored', '=', True)
            ],
            auto_join=True,
            string='Assigned Partner', readonly=True
        ),
    }

    def _prepare_config(self, cr, uid, id, record, vals={}, context=None):
        # Specify the fields contained in the configuration
        res = {
            'model': self._name,
            'res_id': id,
            'stage_id': 'stage_id' in record and record.stage_id.id or False,
            'partner_id': 'partner_id' in record
                          and record.partner_id.id or False,
            'sequence': 'sequence' in record
                        and record.sequence or 'stage_id' in record
                        and record.stage_id.sequence or False,
            'stored': True
        }

        res.update(super(ProjectAssignedPartnerModel, self)._prepare_config(
            cr, uid, id, record, vals=vals, context=context
        ))
        return res


class ProjectProject(orm.Model):

    """
    Add assignment fields in project.project
    """

    _name = 'project.project'
    _inherit = ['project.project', 'project.assigned.partner.model']

    _columns = {
        'manager_partner_id': fields.many2one('res.partner', 'Manager'),
    }

    def _get_external_config(self, cr, uid, record, context=None):
        # Get configuration from stages
        res = {}
        for type in record.type_ids:
            if type.partner_id:
                res[type.id] = self._prepare_config(
                    cr, uid, record.id, type,
                    vals={'stage_id': type.id}, context=context
                )
        return res

    def _get_child_ids(self, cr, uid, ids, context=None):
        # Get project childs
        analytic_ids = {}
        for project in self.browse(cr, uid, ids, context=context):
            analytic_ids[project.analytic_account_id.id] = \
                project.analytic_account_id.id
        return self.search(cr, uid, [
            ('parent_id', 'in', list(analytic_ids))
        ], context=context)

    def _update_stored_config_external_children(
            self, cr, uid, ids, context=None
    ):
        # Trigger update config in tasks linked to this project
        task_obj = self.pool.get('project.task')
        task_ids = task_obj.search(
            cr, uid, [('project_id', 'in', ids)], context=context
        )
        task_obj._update_stored_config(cr, uid, task_ids, context=context)
        return True
