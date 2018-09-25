# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import datetime, time
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProjectTaskScheduling(models.TransientModel):
    _name = 'project.task.scheduling.proposal'
    _description = "Project task scheduling proposal"
    _rec_name = "evaluation"
    _order = 'evaluation'

    description = fields.Char()
    date_start = fields.Datetime()
    date_end = fields.Datetime(
        compute='_compute_end'
    )
    duration = fields.Float(
        compute='_compute_end'
    )
    delayed_tasks = fields.Integer(
        compute='_compute_delayed_tasks'
    )
    evaluation = fields.Float(
        digits=(16, 4),
    )
    task_scheduling_ids = fields.One2many(
        comodel_name='project.task.scheduling',
        inverse_name='proposal_id',
        string="Scheduling list",
        copy=True,
    )
    not_scheduled_task_ids = fields.Many2many(
        comodel_name='project.task',
        string="Not scheduled tasks",
        readonly=True,
    )
    state = fields.Selection(
        selection=[
            ('proposed', 'Proposed'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ],
        default='proposed',
    )

    @api.multi
    @api.depends('task_scheduling_ids.datetime_stop', 'date_start')
    def _compute_end(self):

        def get_key(record):
            return fields.Datetime.from_string(record.datetime_stop)

        for record in self:
            if record.task_scheduling_ids:
                # set date_end
                last_scheduling = max(record.task_scheduling_ids, key=get_key)
                record.date_end = last_scheduling.datetime_stop

                # set duration
                start = fields.Datetime.from_string(record.date_start)
                end = fields.Datetime.from_string(record.date_end)
                record.duration = (end - start).total_seconds() / 3600

    @api.multi
    @api.depends('task_scheduling_ids.delayed')
    def _compute_delayed_tasks(self):
        for r in self:
            r.delayed_tasks = len(r.task_scheduling_ids.filtered('delayed'))

    @api.multi
    def action_timeline_scheduling(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Scheduling proposal'),
            'domain': [('proposal_id', '=', self.id)],
            'res_model': 'project.task.scheduling',
            'view_mode': 'timeline',
            'view_type': 'timeline',
        }

    @api.multi
    def action_approve(self):
        self.ensure_one()
        self.task_scheduling_ids.set_assignation()
        self.search([('id', '!=', self.id)]).action_reject()
        self.state = 'approved'

    @api.multi
    def action_reject(self):
        self.write({'state': 'rejected'})

    @api.multi
    def action_recompute(self):
        self.ensure_one()
        scheduling_wizard = self.env['project.task.scheduling.wizard']
        max_hours_delayed = scheduling_wizard._MAX_HOURS_DELAYED

        hours_dy = task_dy_count = 0
        for assignment in self.task_scheduling_ids:
            task = assignment.task_id
            deadline = fields.Date.from_string(task.date_deadline)
            if deadline:
                deadline_dt = datetime.combine(deadline, time.max)
                stop = fields.Datetime.from_string(assignment.datetime_stop)
                hours_dy += (stop - deadline_dt).total_seconds() / 3600
                is_delayed = assignment.delayed
                task_dy_count += 1 if is_delayed else 0

        if abs(hours_dy) > max_hours_delayed:   # pragma: no cover
            raise ValidationError(_(
                'Maybe some tasks have a very long "Initially Planned Hours" '
                'or Date start is far from the deadline of some tasks'))

        hours_dy += max_hours_delayed
        evaluation = task_dy_count * max_hours_delayed * 2 + hours_dy
        self.evaluation = round(evaluation, 10)

    @api.multi
    def copy(self, default=None):
        if self.search([('state', '=', 'approved')]):
            raise ValidationError(_("You can't duplicate a proposal if there "
                                    "is a proposal approved "))
        return super(ProjectTaskScheduling, self).copy(default=default)
