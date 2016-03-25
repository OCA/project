# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. -
# Jordi Ballester Alomar
# © 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class Project(models.Model):
    _inherit = "project.project"

    @api.multi
    def action_openTasksTreeView(self):
        """
        :return dict: dictionary value for created view
        """
        project = self[0]
        task = self.env['project.task'].search(
            [('project_id', '=', project.id)]
        )
        res = self.env['ir.actions.act_window'].for_xml_id(
            'project_wbs_task', 'action_task_tree_view'
        )
        res['context'] = {
            'default_project_id': project.id,
        }
        res['domain'] = "[('id', 'in', [" + ','.join(
            map(str, task.ids)
        ) + "])]"
        res['nodestroy'] = False
        return res
