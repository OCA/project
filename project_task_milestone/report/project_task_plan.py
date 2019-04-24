# Copyright 2018 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import tools
from odoo import api, fields, models


class ProjectTaskPlan(models.Model):
    _name = 'project.task.plan'
    _description = 'Project Task Plan'
    _auto = False
    _rec_name = 'project_id'

    project_id = fields.Many2one(comodel_name='project.project')
    phase_id = fields.Many2one(comodel_name='project.task.phase')
    start_date = fields.Date()
    end_date = fields.Date()

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
        CREATE or REPLACE VIEW %s as (
            SELECT
              row_number() OVER () AS id,
              project_id,
              phase_id,
              CAST(MIN(date_start) as date) as start_date,
              CAST(MAX(date_end) as date) as end_date
            FROM
              project_task
            GROUP BY
              project_id,
              phase_id
        )""" % (
            self._table))
