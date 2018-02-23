# Copyright 2017 - 2018 Modoolar <info@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import models, fields


class Workflow(models.Model):
    _inherit = 'project.workflow'

    def get_available_transitions(self, task, state):
        transitions = super(Workflow, self).get_available_transitions(
            task, state
        )
        user_groups = frozenset(self.env.user.groups_id.ids or ())
        return [
            x for x in transitions
            if not (x.group_ids and user_groups.isdisjoint(x.group_ids.ids))
        ]


class WorkflowTransition(models.Model):
    _inherit = 'project.workflow.transition'

    group_ids = fields.Many2many(
        comodel_name='res.groups',
        relation='project_task_workflow_transition_groups_rel',
        column1='transition_id',
        column2='group_id',
        string='Groups',
        help='Only defined groups are allowed to make execute this transition.'
             'In case no groups has been defined then everyone can perform '
             'this transition.'
    )
