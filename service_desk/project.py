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

    def onchange_analytic(self, cr, uid, id, analytic_id, context=None):
        res = {}
        model = self.pool.get('account.analytic.account')
        obj = model.browse(cr, uid, analytic_id, context=context)
        if obj:
            # "contact_id" and "department_id" may be provided by other modules
            fldmap = [  # analytic_account field -> task field
                ('partner_id', 'partner_id'),
                ('contact_id', 'location_id'),
                ('department_id', 'department_id')]
            res['value'] = {dest: getattr(obj, orig).id
                            for orig, dest in fldmap
                            if hasattr(obj, orig) and getattr(obj, orig)}
        return res
