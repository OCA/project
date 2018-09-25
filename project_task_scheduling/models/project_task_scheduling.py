# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class ProjectTaskScheduling(models.TransientModel):
    _name = 'project.task.scheduling'
    _description = 'Project task scheduling'
    _rec_name = "task_id"

    proposal_id = fields.Many2one(
        comodel_name='project.task.scheduling.proposal',
        string="Proposal",
        ondelete='cascade',
        required=True,
    )
    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string="Employee",
        required=True,
    )
    task_id = fields.Many2one(
        comodel_name='project.task',
        string="Task",
        required=True,
    )
    datetime_start = fields.Datetime(
        required=True,
    )
    datetime_stop = fields.Datetime(
        required=True,
    )
    delayed = fields.Boolean(
        compute='_compute_delayed',
        default=False,
    )

    @api.multi
    @api.depends('task_id.date_deadline', 'datetime_stop')
    def _compute_delayed(self):
        for rec in self:
            date_deadline = fields.Date.from_string(rec.task_id.date_deadline)
            datetime_stop = fields.Datetime.from_string(rec.datetime_stop)
            if date_deadline and datetime_stop:
                rec.delayed = date_deadline < datetime_stop.date()

    @api.multi
    def set_assignation(self):
        for record in self:
            record.task_id.write({
                'employee_id': record.employee_id.id,
                'user_id': record.employee_id.user_id.id,
                'date_start': record.datetime_start,
                'date_end': record.datetime_stop,
            })
