# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Eficent (<http://www.eficent.com/>)
#               <contact@eficent.com>
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

from openerp import models, fields


class project(models.Model):
    _inherit = "project.project"

    def action_openTasksTreeView(self, cr, uid, ids, context=None):
        """
        :return dict: dictionary value for created view
        """
        if context is None:
            context = {}
        project = self.browse(cr, uid, ids[0], context)
        task_ids = self.pool.get('project.task').search(
            cr, uid, [('project_id', '=', project.id)]
        )
        res = self.pool.get('ir.actions.act_window').for_xml_id(
            cr, uid, 'project_wbs_task', 'action_task_tree_view', context
        )
        res['context'] = {
            'default_project_id': project.id,
        }
        res['domain'] = "[('id', 'in', ["+','.join(map(str, task_ids))+"])]"
        res['nodestroy'] = False
        return res
