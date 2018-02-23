# Copyright 2017 - 2018 Modoolar <info@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import models


class ProjectWorkflowPublisher(models.AbstractModel):
    _inherit = 'project.workflow.publisher'

    def _do_publish(self, old, new, project_id=None, switch=False):

        if not switch:
            old.default_state_ids.unlink()
            new.default_state_ids.write({'workflow_id': old.id})

        return super(ProjectWorkflowPublisher, self)._do_publish(
            old, new, project_id=project_id, switch=switch
        )
