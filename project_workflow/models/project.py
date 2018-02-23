# Copyright 2017 - 2018 Modoolar <info@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import models, fields, api, exceptions, _
from odoo.tools.safe_eval import safe_eval


class Project(models.Model):
    _inherit = 'project.project'

    allow_workflow = fields.Boolean(
        string='Allow Workflow?',
        default=False,
    )

    workflow_id = fields.Many2one(
        comodel_name='project.workflow',
        string='Workflow',
        ondelete="restrict",
        help="Project Workflow"
    )

    @api.onchange('workflow_id')
    def onchange_workflow_id(self):
        """
        When a workflow gets changed we need to collect workflow stages
        and link them to the project as well.
        """
        if self.workflow_id:
            self.type_ids = [x.stage_id.id for x in self.workflow_id.state_ids]
        else:
            self.type_ids = []

    @api.model
    def create(self, vals):
        if not vals.get('allow_workflow', False):
            vals['workflow_id'] = False
            vals['type_ids'] = []
        new = super(Project, self).create(vals)

        if new.allow_workflow and new.workflow_id:
            publisher = self.get_workflow_publisher()
            publisher.publish(
                False, new.workflow_id, project_id=new, switch=True
            )

        return new

    @api.multi
    def write(self, vals):
        if 'allow_workflow' in vals and not vals['allow_workflow']:
            vals['workflow_id'] = False
            vals['type_ids'] = [(5,)]

        return super(Project, self).write(vals)

    def get_workflow_publisher(self):
        return self.env['project.workflow.publisher']

    @api.multi
    def button_run_workflow_wizard(self):
        """
        This method opens ``project_edit_workflow_wizard_action`` wizard.
        :return: Returns ``project_edit_workflow_wizard_action`` action.
        """
        self.ensure_one()
        return self.get_edit_workflow_wizard_action()

    @api.multi
    def get_edit_workflow_wizard_action(self):
        """
        Loads and prepares an action which opens a wizard for setting or
        switching a workflow on current project.
        :return: Returns a prepared action which opens a wizard for setting or
        switching a workflow on current project.
        """
        self.ensure_one()
        workflow_id = self.workflow_id and self.workflow_id.id or False
        action = self.load_edit_workflow_wizard_action()
        action_context = action.get('context', False)
        action_context = action_context and safe_eval(action_context) or {}
        action_context['default_current_workflow_id'] = workflow_id
        action_context['default_project_id'] = self.id
        action['context'] = action_context
        return action

    @api.model
    def load_edit_workflow_wizard_action(self):
        """
        Loads an action which opens a wizard for setting or switching
        a workflow on a project.
        :return: Returns an action which opens a wizard for setting or
        switching a workflow on a project.
        """
        return self.env['ir.actions.act_window'].for_xml_id(
            'project_workflow', 'project_edit_workflow_wizard_action'
        )


class Task(models.Model):
    _inherit = 'project.task'

    allow_workflow = fields.Boolean(
        related="project_id.allow_workflow",
        readonly=True,
    )

    stage_id = fields.Many2one(group_expand='_read_workflow_stage_ids')

    # This field is here just so we can display stage information
    # somewhere else on the task form view and to keep compatibility
    # with other modules like "project_forecast" module.
    wkf_stage_id = fields.Many2one(
        comodel_name='project.task.type',
        related='stage_id',
        string='Workflow Stage',
        readonly=True,
        track_visibility='never',
    )

    workflow_id = fields.Many2one(
        comodel_name='project.workflow',
        related='project_id.workflow_id',
        readonly=True,
    )

    wkf_state_id = fields.Many2one(
        comodel_name='project.workflow.state',
        string='Workflow State',
        compute="_compute_workflow_state",
        store=True
    )

    wkf_state_type = fields.Selection(
        related='wkf_state_id.type',
        string='Wkf State Type'
    )

    @api.model
    def _read_workflow_stage_ids(self, stages, domain, order):
        if 'default_project_id' not in self.env.context:
            return self._read_group_stage_ids(stages, domain, order)

        # TODO: Fix this, it should browse as above user
        project = self.env['project.project'].browse(
            self.env.context['default_project_id']
        )

        if not project.allow_workflow or \
                not project.workflow_id or not project.workflow_id.state_ids:
            return self._read_group_stage_ids(stages, domain, order)

        sorted_state_ids = project.workflow_id.state_ids.sorted(
            key=lambda s: s.kanban_sequence
        )
        stage_ids = [x.stage_id.id for x in sorted_state_ids]
        return stages.browse(stage_ids)

    @api.multi
    @api.depends(
        'stage_id', 'workflow_id', 'project_id.workflow_id',
        'workflow_id.state_ids', 'workflow_id.state_ids.stage_id')
    def _compute_workflow_state(self):
        state = self.env['project.workflow.state']
        with_workflow = self.filtered(lambda r: r.project_id.allow_workflow)

        for task in with_workflow:
            wkf_state_id = False
            if task.project_id.allow_workflow:
                wkf_state = state.search([
                    ('workflow_id', '=', task.workflow_id.id),
                    ('stage_id', '=', task.stage_id.id)
                ])
                wkf_state_id = wkf_state.exists() and wkf_state.id or False

            task.wkf_state_id = wkf_state_id

    @api.cr_uid_context
    def _get_default_stage_id(self):
        if 'default_project_id' not in self.env.context and \
                'project_id' not in self.env.context:
            return False

        project_id = self.env.context.get(
            'default_project_id',
            self.env.context.get('project_id')
        )

        project = self.env['project.project'].browse(project_id)
        if project and project.allow_workflow and project.workflow_id:
            if not project.workflow_id.default_state_id:
                raise exceptions.ValidationError(
                    _(
                        "Project workflow '%s' has no default state."
                        "Please configure the workflow, so that we know what "
                        "default stage should be"
                    ) % project.workflow_id.name
                )
            return project.workflow_id.default_state_id.stage_id.id

        return False

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        project_id = vals.get(
            'project_id', self.env.context.get('default_project_id', False)
        )
        stage_id = self.with_context(
            default_project_id=project_id
        )._get_default_stage_id()

        if stage_id:
            vals['stage_id'] = stage_id

        new = super(Task, self).create(vals)

        if new.project_id.allow_workflow and new.workflow_id:
            new.wkf_state_id.apply(new)

        return new

    @api.multi
    def write(self, vals):
        stage_id = vals.get('stage_id', False)
        if stage_id:
            withoutw = self.filtered(
                lambda k: not (k.workflow_id and k.project_id.allow_workflow)
            )
            if withoutw:
                super(Task, withoutw).write(vals)

            withw = self.filtered(
                lambda k: k.project_id.allow_workflow and k.workflow_id
            )
            stage_id = vals.pop('stage_id')
            for task in withw:
                task.workflow_id.trigger(task, stage_id)
            return super(Task, withw).write(vals)
        else:
            return super(Task, self).write(vals)

    def stage_find(self, section_id, domain=None, order='sequence'):
        project = self.project_id

        if project and project.allow_workflow and project.workflow_id:
            if not project.workflow_id.default_state_id:
                raise exceptions.ValidationError(_(
                    "Project workflow '%s' has no default state."
                    "Please configure the workflow, so that we know what "
                    "default stage should be"
                ) % project.workflow_id.name)
            return project.workflow_id.default_state_id.stage_id.id
        else:
            if not domain:
                domain = []
            return super(Task, self).stage_find(section_id, domain, order)

    @api.model
    def _get_tracked_fields(self, updated_fields):
        tracked_fields = super(Task, self)._get_tracked_fields(updated_fields)

        if 'wkf_stage_id' in tracked_fields:
            del tracked_fields['wkf_stage_id']

        return tracked_fields
