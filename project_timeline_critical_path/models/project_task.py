# Copyright 2018 Onestein
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    critical_path_duration = fields.Float(
        compute='_compute_critical_path_duration',
        store=True
    )

    @api.multi
    @api.depends('date_start',
                 'date_end',
                 'planned_hours',
                 'company_id.critical_path_duration_base')
    def _compute_critical_path_duration(self):
        for task in self:
            base = task.company_id.critical_path_duration_base
            if base == 'date' and task.date_start and task.date_end:
                date_start = fields.Datetime.from_string(task.date_start)
                date_end = fields.Datetime.from_string(task.date_end)
                duration = (date_end - date_start).total_seconds()
                task.critical_path_duration = duration
            elif base == 'planned_hours':
                task.critical_path_duration = task.planned_hours
