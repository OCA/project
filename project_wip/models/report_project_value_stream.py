# -*- coding: utf-8 -*-
# Copyright 2020 Kmee Informática LTDA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, tools


class ReportProjectValueStream(models.Model):

    _name = 'report.project.value.stream'
    _description = 'Report Project Value Stream'
    _auto = False

    project_id = fields.Many2one(
        string='Project',
        comodel_name='project.project',
    )
    in_qty = fields.Integer(
        string='In quantity',
        default=0,
    )
    out_qty = fields.Integer(
        string='Out quantity',
        default=0,
    )
    date_due = fields.Date(
        string='Date',
        default=fields.Date.today,
    )

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""
            CREATE VIEW %s AS
              WITH stages_out AS (
                    SELECT id FROM project_task_type WHERE state='done'),
              stages_in AS (
                    SELECT id FROM project_task_type WHERE state='draft'),
              table_out AS (
                    SELECT MIN(id) AS id, project_id, date_start, 
                    COUNT(*) AS out_qty 
                    FROM project_wip WHERE task_stage_id IN (
                        SELECT id FROM stages_out) 
                    GROUP BY project_id, date_start),
              table_in AS (
                    SELECT MIN(id) AS id, project_id, date_start, 
                    COUNT(*) AS in_qty 
                    FROM project_wip WHERE task_stage_id IN (
                        SELECT id FROM stages_in) 
                    GROUP BY project_id, date_start),
              data AS (SELECT o.id, o.project_id, o.date_start, o.out_qty, 
                        i.in_qty 
                       FROM table_out o INNER JOIN table_in i 
                       ON o.date_start = i.date_start 
                       AND o.project_id = i.project_id)
              SELECT id, project_id, date_start AS date_due, SUM(out_qty) 
                    OVER (PARTITION BY project_id ORDER BY date_start ASC ROWS 
                    BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS out_qty,
                    SUM(in_qty) OVER (PARTITION BY project_id 
                    ORDER BY date_start ASC ROWS BETWEEN UNBOUNDED PRECEDING 
                    AND CURRENT ROW) AS in_qty FROM data;
        """ % self._table)
