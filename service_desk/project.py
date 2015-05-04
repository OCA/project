# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Daniel Reis
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, orm
from openerp import models, api


class ProjectProject(orm.Model):
    _inherit = 'project.project'
    _columns = {
        'use_analytic_account': fields.selection(
            [('no', 'No'), ('yes', 'Optional'), ('req', 'Required')],
            'Use Analytic Account'),
        }
    _defaults = {
        'use_analytic_account': 'no',
        }


class ProjectTask(orm.Model):
    """
    Add related ``Analytic Account`` and service ``Location``.
    A Location can be any Contact Partner of the AA's Partner.
    Other logic is possible, such as maintaining a specific list of service
    addresses for each Contract, but that's out of scope here -
    modules implementing these other possibilities are very welcome.
    """
    _inherit = 'project.task'
    _columns = {
        'analytic_account_id': fields.many2one(
            'account.analytic.account', 'Contract/Analytic',
            domain="[('type','in',['normal','contract'])]"),
        'location_id': fields.many2one(
            'res.partner', 'Location',
            domain="[('parent_id','child_of',partner_id)]"),
        'use_analytic_account': fields.related(
            'project_id', 'use_analytic_account',
            type='char', string="Use Analytic Account"),
        'project_code': fields.related(
            'project_id', 'code', type='char', string="Project Code"),
        }

    def onchange_project(self, cr, uid, id, project_id, context=None):
        # on_change is necessary to populate fields on Create, before saving
        try:
            # try applying a parent's onchange, may it exist
            res = super(ProjectTask, self).onchange_project(
                cr, uid, id, project_id, context=context) or {}
        except AttributeError:
            res = {}

        if project_id:
            obj = self.pool.get('project.project').browse(
                cr, uid, project_id, context=context)
            res.setdefault('value', {})
            res['value']['use_analytic_account'] = (
                obj.use_analytic_account or 'no')
        return res


class ProjectTaskNewAPI(models.Model):
    _inherit = 'project.task'

    @api.onchange('analytic_account_id')
    def onchange_analytic(self):
        contract = self.analytic_account_id
        if contract:
            self.partner_id = contract.partner_id
            self.location_id = contract.contact_id
            if hasattr(contract, 'department_id'):
                self.department_id = contract.department_id
