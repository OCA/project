# Copyright 2017 - 2018 Modoolar <info@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import models, fields, api


class ProjectWorkflowEditWizard(models.TransientModel):
    _name = 'project.workflow.edit.wizard'

    workflow_id = fields.Many2one(
        comodel_name='project.workflow',
    )

    type = fields.Selection(
        selection=[('form', 'Form'), ('diagram', 'Diagram')],
        string='Editor Type',
        default='form',
    )

    @api.multi
    def open_editor(self):
        self.ensure_one()
        action_name = 'project_workflow_%s_edit_action' % self.type
        action = self.env['ir.actions.act_window'].for_xml_id(
            'project_workflow', action_name
        )
        action['res_id'] = self.workflow_id.id
        return action
