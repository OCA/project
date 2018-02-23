# Copyright 2017 - 2018 Modoolar <info@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import models, api


class Task(models.Model):
    _inherit = 'project.task'

    @api.cr_uid_context
    def _get_default_stage_id(self):
        default_stage_id = super(Task, self)._get_default_stage_id()
        if not default_stage_id:
            return False

        project_id = self.env.context.get(
            'default_project_id', self.env.context.get('project_id')
        )

        project = self.env['project.project'].browse(project_id)
        if project and project.workflow_id and \
                project.workflow_id.default_state_ids:

            for default_state in project.workflow_id.default_state_ids:
                if default_state.group_id in self.env.user.groups_id:
                    return default_state.state_id.stage_id.id
        return default_stage_id
