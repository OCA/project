# Copyright 2017 - 2018 Modoolar <info@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import models, fields, api


class ProjectEditWorkflowEWizard(models.TransientModel):
    _name = 'project.edit.workflow.wizard'

    project_id = fields.Many2one(
        comodel_name='project.project',
        string='Project',
    )

    current_workflow_id = fields.Many2one(
        comodel_name='project.workflow',
        string='Current Workflow'
    )

    new_workflow_id = fields.Many2one(
        comodel_name='project.workflow',
        string='New Workflow',
        domain="[('state', '=', 'live'), ('id', '!=', current_workflow_id)]"
    )

    @api.multi
    def apply(self):
        self.ensure_one()

        publisher = self.get_workflow_publisher()
        result = publisher.publish(
            self.current_workflow_id,
            self.new_workflow_id, project_id=self.project_id, switch=True
        )

        if result.has_conflicts:
            return {
                'type': 'ir.actions.act_multi',
                'actions': [{'type': 'ir.actions_act_window_close'},
                            result.action
                            ]
            }

    def get_workflow_publisher(self):
        return self.env['project.workflow.publisher']
