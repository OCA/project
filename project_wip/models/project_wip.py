# Copyright 2019 KMEE INFORMÁTICA LTDA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import datetime

from odoo import api, fields, models, _


class ProjectWip(models.Model):
    _name = 'project.wip'
    _description = 'Project Wip'  # TODO

    project_id = fields.Many2one(
        comodel_name="project.project",
        string="Project",
        required=True,
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
        required=True,
    )

    date_hour_start = fields.Datetime(
        string="Start",
        default=datetime.datetime.now(),
        required=True,
    )

    date_start = fields.Date(
        string="Date Start",
        required=False,
    )

    date_hour_stop = fields.Datetime(
        string="Stop",
        default=datetime.datetime.now(),
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

    task_stage_id = fields.Char(
        string="Stage",
        required=True,
    )

    user_id = fields.Many2one(
        comodel_name="res.users",
        string="User",
        required=True,
    )

    @api.depends('date_hour_stop', 'date_hour_start')
    def _compute_lead_time(self):
        for blocktime in self:
            d1 = fields.Datetime.from_string(blocktime.date_hour_start)
            if blocktime.date_end:
                d2 = fields.Datetime.from_string(blocktime.date_hour_stop)
            else:
                d2 = datetime.datetime.now()
            diff = d2 - d1
            blocktime.lead_time = round(diff.total_seconds() / 60.0, 2)
