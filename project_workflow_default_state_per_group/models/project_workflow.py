# Copyright 2017 - 2018 Modoolar <info@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import models, fields, api


class Workflow(models.Model):
    _inherit = 'project.workflow'

    default_state_ids = fields.One2many(
        comodel_name='project.workflow.default.state',
        inverse_name='workflow_id',
        string='Default States',
        copy=True,
    )

    @api.multi
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        new = super(Workflow, self).copy(default=default)

        states = dict()
        for state in new.state_ids:
            states[state.stage_id.id] = state

        for def_state in new.default_state_ids:
            def_state.write({
                'state_id': states[def_state.state_id.stage_id.id].id
            })

        return new


class WorkflowDefaultStatePerGroup(models.Model):
    _name = 'project.workflow.default.state'
    _order = 'sequence'

    workflow_id = fields.Many2one(
        comodel_name='project.workflow',
        string='Workflow',
        required=True,
        index=True,
        ondelete="cascade",
    )

    group_id = fields.Many2one(
        comodel_name='res.groups',
        string='Group',
        required=True,
    )

    state_id = fields.Many2one(
        comodel_name='project.workflow.state',
        string='State',
        required=True,
    )

    sequence = fields.Integer(
        string='Sequence',
        default=10,
    )

    _sql_constraints = [
        ('unique_group', 'UNIQUE(group_id, workflow_id)',
         'Security group must be unique per workflow!')
    ]
