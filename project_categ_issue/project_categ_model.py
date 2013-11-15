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
        'issue_categ_id': fields.many2one(
            'project.category', 'Root Category for Issues'),
        }


class ProjectIssue(orm.Model):
    _inherit = 'project.issue'

    def onchange_project(self, cr, uid, id, project_id, context=None):
        # on_change is necessary to populate fields on create, before saving
        try:
            res = super(ProjectIssue, self).onchange_project(
                cr, uid, id, project_id, context) or {}
        except AttributeError:
            res = {}

        if project_id:
            obj = self.pool.get('project.project').browse(
                cr, uid, project_id, context=context)
            if obj.issue_categ_id:
                res.setdefault('value', {})
                res['value']['issue_categ_id'] = obj.issue_categ_id.id
        return res

    _columns = {
        'issue_categ_id': fields.related(
            'project_id', 'issue_categ_id', string="Category Root",
            type='many2one', relation='project.category', readonly=True),
        'categ_ids': fields.many2many(
            'project.category', string='Tags',
            domain="[('id','child_of',issue_categ_id)"
                   ",('id','!=',issue_categ_id)]"),
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
