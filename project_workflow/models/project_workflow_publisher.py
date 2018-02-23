# Copyright 2017 - 2018 Modoolar <info@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import models, exceptions, _


class PublisherResult(object):
    WORKFLOW_PUBLISHED = 0
    WORKFLOW_CONFLICTS = 1

    def __init__(self, status, action=None):
        self._status = status
        self._action = action

    @property
    def action(self):
        return self._action

    @property
    def status(self):
        return self._status

    @property
    def is_published(self):
        return self.status == PublisherResult.WORKFLOW_PUBLISHED

    @property
    def has_conflicts(self):
        return self.status == PublisherResult.WORKFLOW_CONFLICTS

    @staticmethod
    def success():
        return PublisherResult(PublisherResult.WORKFLOW_PUBLISHED)

    @staticmethod
    def conflict(action):
        return PublisherResult(PublisherResult.WORKFLOW_CONFLICTS, action)


class ProjectWorkflowPublisher(models.AbstractModel):
    _name = 'project.workflow.publisher'

    def publish(self, old, new, mappings=None, project_id=None, switch=False):
        if not new:
            raise exceptions.ValidationError(_(
                'You have to provide the new workflow!')
            )

        if not old and not project_id:
            raise exceptions.ValidationError(_(
                "In case old workflow is not present, "
                "you need to provide project to which, "
                "a new workflow will be applied!"
            ))

        diff = self.diff(old, new, project_id, switch)

        if diff['is_empty']:
            return self._do_publish(
                old, new, project_id=project_id, switch=switch
            )

        if self._do_map(diff, mappings, old, new, project_id):
            return self._do_publish(
                old, new, project_id=project_id, switch=switch
            )

        return PublisherResult.conflict(
            self._get_wizard_action(
                self._build_mapping_wizard(
                    old, new, diff, project_id=project_id, switch=switch
                )
            )
        )

    def diff(self, old, new, project_id, switch):
        """
        This method will return compare result between old and new workflow
        or project and workflow
        :param old: The old workflow
        :param new: The new workflow
        :param project_id: The project on which we want to apply
        the new workflow.
        :return: Returns result of this comparison
        """
        result = dict()

        def get_states(obj, is_workflow=True):
            if is_workflow:
                states = set()
                for state in obj.state_ids:
                    states.add(state.stage_id.id)
                return states
            else:
                self.env.cr.execute(
                    """
                    SELECT distinct(stage_id)
                    FROM project_task
                    WHERE project_id IN %s
                    """, (tuple([obj.id]),)
                )
                return set([x[0] for x in self.env.cr.fetchall()])

        # Following stages has been removed from the workflow
        # project_ids = []
        if old and new:
            removed_stages = get_states(old) - get_states(new)
            project_ids = switch and [project_id.id] or old.project_ids.ids
        else:
            removed_stages = get_states(project_id, False) - get_states(new)
            project_ids = [project_id.id]

        # Now we need to see is any of removed stages requires mapping.
        hits = []

        for stage_id in removed_stages:
            task_count = self.env['project.task'].search([
                ('project_id', 'in', project_ids), ('stage_id', '=', stage_id)
            ], count=True)

            if task_count > 0:
                hits.append({'id': stage_id or False, 'count': task_count})

        result['stages'] = hits
        result['is_empty'] = len(hits) == 0
        return result

    def _do_map(self, result, mappings, old, new, project_id=None):
        if not self._can_be_mapped(result, mappings):
            return False

        # project_ids = []
        if old and new:
            project_ids = old.project_ids.ids
        else:
            project_ids = [project_id.id]

        if 'stages' in mappings:
            for mapping in mappings['stages']:
                tasks = self.env['project.task'].search([
                    ('project_id', 'in', project_ids),
                    ('stage_id', '=', mapping['from'])])
                tasks._write({'stage_id': mapping['to']})
        return True

    def _can_be_mapped(self, result, mappings):
        if not mappings:
            return False

        if 'stages' in mappings:
            data = set([m['from'] for m in mappings['stages']])
            for stage in result['stages']:
                if stage['id'] not in data:
                    return False

        return True

    def _do_publish(self, old, new, project_id=None, switch=False):
        if switch:
            stage_ids = [(6, 0, [x.stage_id.id for x in new.state_ids])]

            if project_id:
                project_id.write({
                    'workflow_id': new.id,
                    'type_ids': stage_ids
                })
            else:
                old.project_ids.write({
                    'workflow_id': new.id,
                    'type_ids': stage_ids
                })
        else:
            data = {}
            if not new.name.startswith('Draft'):
                data['name'] = new.name

            if new.description != old.description:
                data['description'] = new.description

            data['default_state_id'] = False
            if new.default_state_id:
                data['default_state_id'] = new.default_state_id.id

            if data:
                old.write(data)

            old.transition_ids.unlink()
            old.state_ids.unlink()
            new.transition_ids.write({'workflow_id': old.id})
            new.state_ids.write({'workflow_id': old.id})

            new.unlink()

        return PublisherResult.success()

    def _build_mapping_wizard(self, old, new, result, project_id=None,
                              switch=False):
        # Create Wizard
        wizard = self.env['project.workflow.stage.mapping.wizard'].create(
            self._prepare_mapping_wizard(
                old, new, project_id=project_id, switch=switch
            )
        )

        # Bind stages for mapping
        wstages = []
        for stage in result['stages']:
            wstage = self.env['project.workflow.stage.mapping.wizard.stage']\
                .create(self._prepare_deleted_wizard_stage(wizard, stage))

            wstages.append(wstage)

        # Bind list of possible stages
        for state in new.state_ids:
            self.env['project.workflow.stage.mapping.wizard.stage'].create(
                self._prepare_possible_stage(wizard, state)
            )

        # Create finite mapping list
        for wstage in wstages:
            self.env['project.workflow.stage.mapping.wizard.line'].create(
                self._prepare_wizard_line(wizard, wstage)
            )

        return wizard

    def _prepare_mapping_wizard(self, old, new, project_id, switch):
        """
        Prepares data
        :param old:
        :param new:
        :param switch:
        :return:
        """
        return {
            'from_id': old.exists() and old.id or False,
            'to_id': new.id,
            'project_id': project_id and project_id.id or False,
            'switch': switch,
            'from_diagram': self.env.context.get('diagram', False)
        }

    def _prepare_deleted_wizard_stage(self, wizard, stage):
        """
        Prepare data to create deleted wizard stage.
        :param wizard: The wizard to which this stage belongs to.
        :param stage: The deleted stage
        :return: Returns prepared data
        """
        return {
            'wizard_id': wizard.id,
            'type': 'from',
            'task_count': stage['count'],
            'stage_id': stage['id'],
        }

    def _prepare_possible_stage(self, wizard, state):
        return {
            'wizard_id': wizard.id,
            'type': 'to',
            'stage_id': state.stage_id.id,
        }

    def _prepare_wizard_line(self, wizard, from_state):
        return {
            'wizard_id': wizard.id,
            'from_id': from_state.id,
        }

    def _get_wizard_action(self, wizard):
        action = self.env['ir.actions.act_window'].for_xml_id(
            'project_workflow', 'project_workspace_mapping_wizard_action')
        action['res_id'] = wizard.id
        return action
