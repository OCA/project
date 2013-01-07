# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2012 Daniel Reis
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

from osv import fields, osv


class task(osv.osv):
    _inherit = "project.task"
    _columns = {
        #new
        'material_ids': fields.one2many('project.task.materials', 'task_id', 'Materials used'),
        #modified
        'project_id': fields.many2one('project.project', 'Project', ondelete='set null', select="1"
                                      , required=True), #project is now required
    }
task()


class project_task_materials(osv.osv):
    _name = "project.task.materials"
    _description = "Project Task Materials Used"
    _inherits = {'account.analytic.line': 'line_id'}

    def _getAnalyticJournal(self, cr, uid, context=None):
        md = self.pool.get('ir.model.data')
        try:
            return  md.get_object_reference(cr, uid, 'project_task_materials', 'materials_analytic_journal')[1]
        except ValueError:
            pass
        return False

    _columns = {
        'task_id': fields.many2one('project.task', 'Task', ondelete='cascade', required=True),
        'line_id': fields.many2one('account.analytic.line', 'Analytic line', ondelete='cascade', required=True),
    }
#    _defaults = {
#        'journal_id': lambda self, cr, uid, ctx: _getAnalyticJournal,
#    }

    def create(self, cr, uid, vals, *args, **kwargs):
        task_mdl = self.pool.get('project.task')
        task_doc = task_mdl.browse( cr, uid, [vals['task_id']] )[0]
        prod_mdl = self.pool.get('product.product')
        prod_doc = prod_mdl.browse( cr, uid, [vals['product_id']] )[0]
        vals.update({
            'journal_id':     self._getAnalyticJournal(cr, uid),
            #Task defaults:
            'name':           task_doc.name,
            'account_id':     task_doc.project_id.analytic_account_id.id,
            'to_invoice':     task_doc.project_id.analytic_account_id.to_invoice.id,
            #Product defaults:
            'product_uom_id': prod_doc.uom_id.id,
            'general_account_id': prod_doc.product_tmpl_id.property_account_expense.id
                                  or prod_doc.categ_id.property_account_expense_categ.id,
            })
        return super(project_task_materials, self).create(cr, uid, vals, *args, **kwargs)

project_task_materials()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
