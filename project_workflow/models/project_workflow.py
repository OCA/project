# Copyright 2017 - 2018 Modoolar <info@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import models, fields, api, exceptions, _
from odoo.tools import safe_eval


class Workflow(models.Model):
    _name = 'project.workflow'
    _description = 'Project Workflow'

    name = fields.Char(
        string='Name',
        required=True,
        help="The name of the workflow. It has to be unique!"
    )

    description = fields.Html(
        string='Description',
        help="Describe this workflow for your colleagues ..."
    )

    state_ids = fields.One2many(
        comodel_name='project.workflow.state',
        inverse_name='workflow_id',
        string='States',
        copy=True,
        help="The list of all possible states a task can be in."
    )

    default_state_id = fields.Many2one(
        comodel_name='project.workflow.state',
        string="Default state",
        help="Stage from this state will be set by default if not specified "
             "when creating task.",
    )

    transition_ids = fields.One2many(
        comodel_name='project.workflow.transition',
        inverse_name='workflow_id',
        ondelete="cascade",
        string='Transitions',
        copy=True,
        help="The list of all state transitions."
    )

    project_ids = fields.One2many(
        comodel_name='project.project',
        inverse_name='workflow_id',
        string='Projects',
        help="The list of related projects."
    )

    state = fields.Selection(
        selection=[('draft', 'Draft'), ('live', 'Live')],
        string='State',
        default='draft',
        copy=False,
        index=True,
    )

    original_id = fields.Many2one(
        comodel_name='project.workflow',
        string='Origin',
        ondelete="cascade",
    )

    original_name = fields.Char(
        string='Original',
        related='original_id.name',
        readonly=True,
    )

    edit_ids = fields.One2many(
        comodel_name='project.workflow',
        inverse_name='original_id',
        string='Drafts',
    )

    edit_count = fields.Integer(
        string='Edit Count',
        compute="_compute_edit_count",
    )

    stage_ids = fields.Many2many(
        comodel_name='project.task.type',
        compute="_compute_stage_ids",
        string='All workflow task stages'
    )

    @api.multi
    def _compute_stage_ids(self):
        for record in self:
            record.stage_ids = [x.stage_id.id for x in record.state_ids]

    _sql_constraints = [
        ('unique_workflow_name', 'UNIQUE(original_id, name)',
         'Project workflow with this name already exists!')
    ]

    @api.depends('edit_ids')
    @api.multi
    def _compute_edit_count(self):
        for workflow in self:
            workflow.edit_count = len(workflow.edit_ids)

    @api.multi
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        new = super(Workflow, self).copy(default=default)

        states = dict()
        for state in new.state_ids:
            states[state.stage_id.id] = state

        def get_new_default_state():
            for state in new.state_ids:
                if state.stage_id.id == self.default_state_id.stage_id.id:
                    return state.id
            return False

        new_update = {
            'default_state_id': get_new_default_state()
        }
        for transition in new.transition_ids:
            src_id = states[transition.src_id.stage_id.id].id
            dst_id = states[transition.dst_id.stage_id.id].id
            transition.write({'src_id': src_id, 'dst_id': dst_id})

        default = default or {}
        if 'name' not in default:
            new_update['name'] = "%s (COPY)" % new.name

        new.write(new_update)

        return new

    @api.multi
    def unlink(self):
        for workflow in self:
            if len(workflow.project_ids) != 0:
                projects = [p.name for p in workflow.project_ids]
                raise exceptions.ValidationError(_(
                    "You are not allowed do delete this workflow because it is"
                    " being used by the following projects: %s"
                    ) % projects
                )
        return super(Workflow, self).unlink()

    @api.multi
    def is_live(self):
        """
        Gets a value indicating whether this workflow has been published or not
        :return: Returns a value indicating whether this workflow has been
        published or not.
        """
        self.ensure_one()
        return self.state == 'live'

    @api.multi
    def is_draft(self):
        """
        Gets a value indicating whether this workflow has been published or not
        :return: Returns a value indicating whether this workflow has been
        published or not.
        """
        self.ensure_one()
        return self.state == 'draft'

    def find_transition(self, task, stage_id):
        def check_transition(t, s):
            return t.workflow_id and t.stage_id.id != s

        if not check_transition(task, stage_id):
            return False

        transitions = self.find_transitions(
            task, task.stage_id.id, group_by='stage_id'
        )

        if stage_id not in transitions:
            raise exceptions.ValidationError(_(
                "Transition to this state is not supported "
                "from the current task state!\n"
                "Please refer to the project workflow '%s' to "
                "see all possible transitions from "
                "the current state or you could view task in "
                "form view and see possible transitions"
                "from there."
            ) % self.name)

        return transitions[stage_id]

    @api.multi
    def trigger(self, task, target_stage_id):
        self.ensure_one()

        transition = self.find_transition(task, target_stage_id)

        if not transition:
            return

        if transition['global']:
            self.env['project.workflow.state'].browse(
                transition['state_id']
            ).apply(task)
        else:
            self.env['project.workflow.transition'].browse(
                transition['transition_id']
            ).apply(task)

    @api.model
    def get_state_transitions(self, workflow_id, stage_id, task_id):
        if not workflow_id or not stage_id:
            return []

        workflow = self.browse(workflow_id)
        task = self.env['project.task'].browse(task_id)

        transitions = workflow.find_transitions(task, stage_id)
        return transitions

    def find_transitions(self, task, stage_id, group_by=None):
        def get_state(stage_id):
            for state in self.state_ids:
                if state.stage_id.id == stage_id:
                    return state
            return False

        state = get_state(stage_id)
        if not state:
            return []

        transitions = []
        if state.is_global:
            for transition in self.transition_ids:
                transitions.append(self._populate_state_for_widget(transition))

        else:
            transitions = [
                self._populate_state_for_widget(x)
                for x in self.get_available_transitions(task, state)
            ]

        global_states = self.state_ids.filtered(
            lambda r: r.is_global and r.stage_id.id != stage_id
        )

        for state in global_states:
            transitions.append({
                'global': True,
                'state_id': state.id,
                'name': state.name,
                'description': state.description,
                'confirmation': False,
                'id': state.stage_id.id,
                'sequence': state.sequence,
            })

        if group_by and group_by == 'stage_id':
            grouped_by = dict()
            for transition in transitions:
                grouped_by[transition['id']] = transition
            transitions = grouped_by
        return transitions

    def get_available_transitions(self, task, state):
        return state.out_transitions

    @api.model
    def _populate_state_for_widget(self, transition):
        return {
            'global': False,
            'transition_id': transition.id,
            'name': transition.name,
            'desc': transition.description,
            'confirmation': transition.user_confirmation,
            'id': transition.dst_id.stage_id.id,
            'sequence': transition.dst_id.sequence,
        }

    @api.multi
    def export_workflow(self):
        self.ensure_one()
        wizard = self.env['project.workflow.export.wizard'].create(
            {'workflow_id': self.id}
        )
        return wizard.button_export()

    @api.multi
    def edit_workflow(self):
        self.ensure_one()

        # By default we want to edit current workflow
        edit = self

        # For live workflow we want to create working copy or reuse it.
        if self.is_live():
            if len(self.edit_ids) == 0:
                edit = self.copy({
                    'name': _("Draft Version of '%s'") % self.name,
                    'state': 'draft',
                    'default_state_id': self.default_state_id.id,
                    'original_id': self.id
                })
                pass
            else:
                edit = self.edit_ids[0]

        action = self.env['ir.actions.act_window'].for_xml_id(
            'project_workflow', 'project_workflow_diagram_edit_action'
        )

        ctx = safe_eval(action['context'])

        ctx['active_id'] = edit.id
        ctx['active_ids'] = [edit.id]
        action['res_id'] = edit.id

        action['context'] = ctx

        return action

    @api.multi
    def publish_workflow(self):
        self.ensure_one()

        if self.is_draft() and self.original_id:
            publisher = self.get_workflow_publisher()
            result = publisher.publish(self.original_id, self)

            if result.has_conflicts:
                from_diagram = self.env.context.get('diagram', False)
                action = result.action
                action_context = safe_eval(action.get('context', '{}'))
                action_context['default_from_diagram'] = from_diagram
                action['context'] = action_context
                return action

        else:
            self.state = 'live'

    def get_workflow_publisher(self):
        return self.env['project.workflow.publisher']

    # This is a workaround!
    # This should be checked once we upgrade to a newer version of Odoo.
    # because it does not make sense for context not to be allowed on
    # tree view buttons.
    @api.multi
    def discard_working_copy_from_tree(self):
        self.ensure_one()
        self.with_context(original=True, origin='tree').discard_working_copy()

    @api.multi
    def discard_working_copy(self):
        self.ensure_one()

        if self.env.context.get('original', False):
            for edit in self.edit_ids:
                edit.unlink()
            return {'type': 'ir.actions.act_view_reload'}

        self.unlink()

        return {
            'type': 'ir.actions_act_multi',
            'actions': [
                {'type': 'history_back'},
                {'type': 'ir.actions_act_view_reload'},
            ]
        }

    @api.multi
    def get_formview_id(self):
        return self.env.ref("project_workflow.project_workflow_form").id

    @api.multi
    def get_formview_action(self):
        view_id = self.get_formview_id()
        ctx = dict(self._context)
        ctx['edit'] = False
        ctx['create'] = False

        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'target': 'current',
            'res_id': self.id,
            'context': ctx,
        }


class WorkflowState(models.Model):
    _name = 'project.workflow.state'
    _description = 'Project Workflow State'
    _order = 'sequence'

    stage_id = fields.Many2one(
        comodel_name='project.task.type',
        string='Stage',
        required=True,
        ondelete="restrict",
        index=True,
    )

    name = fields.Char(
        string='Name',
        related='stage_id.name',
        requried=True,
    )

    description = fields.Text(
        string='Description',
        related='stage_id.description',
        requried=True,
    )

    workflow_id = fields.Many2one(
        comodel_name='project.workflow',
        string='Workflow',
        required=True,
        ondelete="cascade",
    )

    is_default = fields.Boolean(
        string="Is default",
        compute="_compute_is_default",
        inverse="_inverse_is_default",
    )

    is_global = fields.Boolean(
        string='Is global?',
        default=False,
        help="When checked it will allow all transitions from/to this state.",
    )

    out_transitions = fields.One2many(
        comodel_name='project.workflow.transition',
        inverse_name='src_id',
        string='Outgoing Transitions'
    )

    in_transitions = fields.One2many(
        comodel_name='project.workflow.transition',
        inverse_name='dst_id',
        string='Incoming Transitions'
    )

    type = fields.Selection(
        selection=[
            ('todo', 'ToDo'),
            ('in_progress', 'In Progress'),
            ('done', 'Done'),
        ],
        default='in_progress',
        string='Type',
        required=True,
    )

    xpos = fields.Integer(
        string='X',
        default=50,
        copy=True,
    )

    ypos = fields.Integer(
        string='Y',
        default=50,
        copy=True,
    )

    sequence = fields.Integer(
        string='Sequence',
        default=0,
    )

    kanban_sequence = fields.Integer(
        string='Kanban Sequence',
        default=0,
    )

    _sql_constraints = [
        ('unique_state_stage', 'UNIQUE(workflow_id,stage_id)',
         'This state already exists!'
         )
    ]

    @api.multi
    def _compute_is_default(self):
        for record in self:
            default_state = record.workflow_id.default_state_id
            record.is_default = default_state.id == record.id

    @api.multi
    def _inverse_is_default(self):
        for record in self:
            if record.is_default:
                record.workflow_id.default_state_id = record.id

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        state_ids = self.env.context.get('state_ids', False)
        if state_ids:
            args = args or []
            args.append(('id', 'in', [x[1] for x in state_ids]))

        return super(WorkflowState, self).name_search(
            name, args, operator, limit
        )

    def apply(self, task):
        task._write({'stage_id': self.stage_id.id})


class WorkflowTransition(models.Model):
    _name = 'project.workflow.transition'
    _description = 'Project Workflow Transition'

    name = fields.Char(
        string='Name',
        required=True,
    )

    description = fields.Html(
        string='Description'
    )

    workflow_id = fields.Many2one(
        comodel_name='project.workflow',
        string='Workflow',
        required=True,
        ondelete="cascade",
    )

    src_id = fields.Many2one(
        comodel_name='project.workflow.state',
        string='Source Stage',
        required=True,
        index=True,
        ondelete="cascade",
    )

    dst_id = fields.Many2one(
        comodel_name='project.workflow.state',
        string='Destination Stage',
        required=True,
        index=True,
        ondelete="cascade",
    )

    user_confirmation = fields.Boolean(
        string='User Confirmation?',
        default=False
    )

    _sql_constraints = [
        ('unique_src_dst', 'UNIQUE(workflow_id,src_id,dst_id)',
         'This transition already exists!'),
    ]

    def apply(self, task):
        self.dst_id.apply(task)
