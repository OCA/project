# Copyright 2019 KMEE INFORMÁTICA LTDA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import datetime

from odoo import api, fields, models, _


class ProjectWip(models.Model):
    _name = 'project.wip'
    _description = 'Project Wip'  # TODO

    project_id = fields.Many2one(
        comodel_name="project.project",
        related="task_id.project_id",
        string="Project",
        required=False,
    )

    task_id = fields.Many2one(
        comodel_name="project.task",
        string="Task",
        required=True,
    )

    state = fields.Selection(
        string="State",
        selection=[
            ('running', 'Running'),
            ('closed', 'Closed'),
        ],
        default='running',
        required=True,
    )

    date_hour_start = fields.Datetime(
        string="Start",
        default=fields.Datetime.now,
        required=True,
    )

    date_start = fields.Date(
        string="Date Start",
        # related="date_hour_start",
        required=False,
    )

    date_hour_stop = fields.Datetime(
        string="Stop",
        required=False,
    )

    date_stop = fields.Date(
        string="Date Stop",
        required=False,
    )

    lead_time = fields.Float(
        string='Duration',
        compute='_compute_lead_time',
        store=True
    )

    task_stage_id = fields.Many2one(
        comodel_name="project.task.type",
        string="Stage",
        required=False,
    )

    user_id = fields.Many2one(
        comodel_name="res.users",
        string="User",
        required=False,
    )

    @api.depends('date_hour_stop', 'date_hour_start')
    def _compute_lead_time(self):
        for blocktime in self:
            d1 = fields.Datetime.from_string(blocktime.date_hour_start)
            if blocktime.date_hour_stop:
                d2 = fields.Datetime.from_string(blocktime.date_hour_stop)
            else:
                d2 = datetime.datetime.now()
            diff = d2 - d1
            blocktime.lead_time = round(diff.total_seconds() / 60.0, 2)

    def stop(self):
        for record in self.filtered(lambda o: o.state == 'running'):
            record.sudo().write({
                'state': 'closed',
                'date_hour_stop': fields.Datetime.now(),
            })

    def start(self, task_id, stage_id):
        stage_id = self.env['project.task.type'].browse(stage_id)
        if stage_id.state in ['open', 'pending']:
            self.env['project.wip'].sudo().create({
                'task_id': task_id,
                'task_stage_id': stage_id.id,
            })
