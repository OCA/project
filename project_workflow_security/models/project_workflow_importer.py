# Copyright 2017 - 2018 Modoolar <info@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import models


class WorkflowImporter(models.AbstractModel):
    _inherit = 'project.workflow.importer'

    def prepare_transition(self, transition, states):
        data = super(WorkflowImporter, self).prepare_transition(
            transition, states
        )
        data['group_ids'] = [(6, 0, self.prepare_security_groups(transition))]
        return data

    def prepare_security_groups(self, transition):
        groups = []
        for group in transition.get('groups', []):
            group_id = self.prepare_security_group(group)
            if group_id:
                groups.append(group_id)
        return groups

    def prepare_security_group(self, group):
        return self.env.ref(group['xml_id']).id
