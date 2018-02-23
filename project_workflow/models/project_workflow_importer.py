# Copyright 2017 - 2018 Modoolar <info@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

import logging
from odoo import models, exceptions, _

_logger = logging.getLogger(__name__)


class WorkflowImporter(models.AbstractModel):
    _name = 'project.workflow.importer'

    def _load_task_stages(self):
        """
        Creates name based dictionary out of all ``project.task.type`` records.
        :return: Returns stage dictionary
        """
        stages = dict()
        for stage in self.env['project.task.type'].search([]):
            stages[self.get_stage_name(stage)] = stage
        return stages

    def get_stage_name(self, stage):
        return stage.name

    def run(self, reader, stream):
        """
        Runs import process of the given project workflow data stream.
        :param stream: The stream of data to be imported.
        :param reader: The stream data reader.
        :return: Returns
        """
        if reader is None:
            raise exceptions.ValidationError(
                _("Importer can not run without provided data reader!")
            )

        workflow = reader.wkf_read(stream)
        return self._import_workflow(workflow)

    def _import_workflow(self, workflow):
        """
        Imports given workflow into odoo database
        :param workflow: The project workflow to be imported.
        :return: Returns instance of the imported project workflow.
        """

        all_stages = self._load_task_stages()

        stages_to_create = []
        for state in workflow['states']:
            if self.get_state_name(state) not in all_stages:
                stages_to_create.append(state)

        # Create new stages and register them
        for state in stages_to_create:
            stage = self.create_stage(self.prepare_task_stage(state))
            all_stages[stage.name] = stage

        state_prep = self.prepare_state
        state_name = self.get_state_name

        wkf = self.create_workflow(self.prepare_workflow(workflow, [
            (0, 0, state_prep(state, all_stages[state_name(state)].id))
            for state in workflow['states']
        ]))

        def get_state(stage_id):
            for state in wkf.state_ids:
                if state.stage_id == stage_id:
                    return state
            return False

        wkf.default_state_id = get_state(
            all_stages[workflow['default_state']]
        ).id

        states = dict()
        for state in wkf.state_ids:
            states[state.name] = state

        transitions = [
            (0, 0, self.prepare_transition(t, states))
            for t in workflow['transitions']
        ]

        wkf.write({'transition_ids': transitions})
        return wkf

    def create_stage(self, stage_data):
        return self.env['project.task.type'].create(stage_data)

    def create_workflow(self, workflow_data):
        return self.env['project.workflow'].create(workflow_data)

    def prepare_workflow(self, workflow, state_ids):
        """
        Prepares ``project.workflow`` data.
        :param workflow: The workflow to be mapped to the odoo workflow
        :param state_ids: The list of already odoo mapped states.
        :return: Returns dictionary with workflow data ready to be saved
        within odoo database.
        """
        return {
            'name': workflow['name'],
            'description': workflow['description'],
            'state_ids': state_ids,
        }

    def prepare_task_stage(self, state):
        """
        Prepares ``project.task.type`` dictionary for saving.
        :param state: Parsed state dictionary.
        :return: Returns prepared ``project.task.type`` values.
        """
        return {
            'name': state['name'],
            'description': state['description'],
        }

    def get_state_name(self, state):
        return state['name']

    def prepare_state(self, state, stage_id):
        """
        Prepares ``project.workflow.state`` dictionary for saving.
        :param state: Parsed state dictionary.
        :return: Returns prepared ``project.workflow.state`` values.
        """
        return {
            'stage_id': stage_id,
            'sequence': state['sequence'],
            'kanban_sequence': state['kanban_sequence'],
            'type': state['type'],
            'xpos': state['xpos'],
            'ypos': state['ypos'],
        }

    def prepare_transition(self, transition, states):
        """
        Prepares ``project.workflow.transition`` dictionary for saving.
        :param transition: Parsed transition dictionary.
        :param states: Dictionary of state browse objects.
        :return: Returns prepared ``project.workflow.transition`` values.
        """
        return {
            'name': transition['name'],
            'description': transition['description'],
            'src_id': states[transition['src']].id,
            'dst_id': states[transition['dst']].id,
            'user_confirmation': transition['confirmation'],
        }
