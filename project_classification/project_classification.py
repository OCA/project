# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Joël Grand-guillaume (Camptocamp)
#    Copyright 2011 Camptocamp SA
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
from openerp.osv import orm, fields


class ProjectClassification(orm.Model):
    _name = "project.classification"
    _description = "Project classification"

    _columns = {
        'name': fields.char('Classification Name', required=True, size=64),
        'project_id':
        fields.many2one('account.analytic.account',
                        'Parent project',
                        help="The parent project that will be set when "
                        "choosing this classification in a project.",
                        required=True),
        'to_invoice': fields.many2one('hr_timesheet_invoice.factor',
                                      'Reinvoice Costs',
                                      help="Fill this field if you plan to "
                                      "automatically generate invoices based "
                                      "on the costs in this classification"),
        'currency_id': fields.many2one('res.currency', 'Currency'),
        'user_id': fields.many2one('res.users', 'Account Manager'),
        'pricelist_id': fields.many2one('product.pricelist',
                                        'Sale Pricelist',),
        }


class ProjectProject(orm.Model):
    _inherit = "project.project"

    def _child_project_compute(self, cr, uid, ids, name, arg, context=None):
        result = {}.fromkeys(ids, [])
        if context is None:
            context = {}

        for project in self.browse(cr, uid, ids, context=context):
            child_projects = []
            # child_complete_ids are account.analytic.account
            for account_child in project.child_complete_ids:
                if not account_child.project_ids:
                    continue
                child_projects += account_child.project_ids

            result[project.id] = [child_project.id for child_project
                                  in child_projects]
        return result

    def onchange_classification_id(self, cr, uid, ids, classification_id):
        projclass = self.pool.get('project.classification')
        classification = projclass.browse(cr, uid, classification_id)
        return {'value':
                {'parent_id': classification.project_id.id,
                 'to_invoice': classification.to_invoice.id or False,
                 'currency_id': classification.currency_id.id or False,
                 'user_id': classification.user_id.id or False,
                 'pricelist_id': classification.pricelist_id.id or False}}

    _columns = {
        'classification_id':
        fields.many2one('project.classification', 'Classification',
                        help="This will automatically set the parent "
                        "project as well as other default values define "
                        "for this kind project (like pricelist, "
                        "invoice factor,..)",
                        required=True),
        'child_project_complete_ids':
        fields.function(_child_project_compute,
                        relation='project.project',
                        method=True,
                        string="Project Hierarchy", type='many2many'),
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
