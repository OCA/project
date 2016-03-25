# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. -
# Jordi Ballester Alomar
# © 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


#class TaskType(models.Model):
#    _inherit = 'project.task.type'
#
#    _TASK_STATE = [('draft', 'New'),('open', 'In Progress'),('pending', 'Pending'), ('done', 'Done'), ('cancelled', 'Cancelled')]
#
#    state = fields.Selection(_TASK_STATE, 'Related Status', required=False,
#                        help="The status of your document is automatically changed regarding the selected stage. " \
#                            "For example, if a stage is related to the status 'Close', when your document reaches this stage, it is automatically closed.")


class Task(models.Model):
    _inherit = 'project.task'

#    @api.model
#    def _get_composition_mode_selection(self):
#        return [('comment', 'Post on a document'),
#                ('mass_mail', 'Email Mass Mailing'),
#                ('mass_post', 'Post on Multiple Documents')]
#
#    composition_mode = fields.Selection(selection=_get_composition_mode_selection, string='Composition mode', default='comment')

    @api.multi
    def _project_complete_wbs_name(self):
        if not self._ids:
            return []
        res = []
        data_project = []
        for task in self:
            if task.project_id:
                data_project = task.project_id.complete_wbs_name
            if data_project:
                res.append((task.id, data_project))
            else:
                res.append((task.id, ''))
        return dict(res)

    @api.multi
    def _project_complete_wbs_code(self):
        if not self._ids:
            return []
        res = []
        data_project = []
        for task in self:
            if task.project_id:
                data_project = task.project_id.complete_wbs_code
            if data_project:
                res.append((task.id, data_project))
            else:
                res.append((task.id, ''))
        return dict(res)

    analytic_account_id = fields.\
        Many2one(related='project_id.analytic_account_id',
                 relation='account.analytic.account',
                 string='Analytic Account', store=True, readonly=True)
    project_complete_wbs_code = fields.\
        Char('Full WBS Code', related='analytic_account_id.complete_wbs_code',
             readonly=True)
    project_complete_wbs_name = fields.\
        Char('Full WBS Name', related='analytic_account_id.complete_wbs_name',
             readonly=True)
