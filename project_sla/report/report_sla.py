# -*- coding: utf-8 -*-
# © 2013 Daniel Reis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api
from odoo.addons.project_sla.models.project_sla_control import SLA_STATES
from odoo import tools


class ReportSla(models.Model):

    _name = "project.sla.report"
    _description = "Project SLA report"
    _auto = False
    _order = ('date_year, date_quarter, date_month, date_week, sla_closed, '
              'sla_state')

    # Overridden to automaticaly calculate correct achieved percent for any
    # group result
    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None,
                   orderby=False, lazy=True):
        res = super(ReportSla, self).read_group(
            domain, fields, groupby, offset, limit, orderby, lazy)
        for gres in res:
            if 'achieved_count' in gres and 'total_count' in gres:
                acount = float(gres['achieved_count'])
                tcount = float(gres['total_count'])
                gres['achieved_perc'] = round((acount / tcount) * 100, 2)
        return res

    @api.multi
    @api.depends('achieved_count', 'total_count')
    def _compute_achieved_percent(self):
        for line in self:
            acount = float(line.achieved_count)
            tcount = float(line.total_count)
            line.achieved_perc = round((acount / tcount) * 100, 2)

    document_model_id = fields.Many2one('ir.model', string='Document Model')
    sla_name = fields.Char('SLA Name')
    sla_line_name = fields.Char('SLA Line Name')
    sla_state = fields.Selection(SLA_STATES, 'SLA State')
    date_year = fields.Char('Year')
    date_quarter = fields.Char('Quarter')
    date_month = fields.Char('Month')
    date_week = fields.Char('Week')
    sla_closed = fields.Boolean('Is Closed')
    total_count = fields.Integer('Total Count')
    achieved_count = fields.Integer('Achieved Count')
    failed_count = fields.Integer('Failed Count')
    achieved_perc = fields.Float(
        compute="_compute_achieved_percent", string='Achieved Percent')

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'project_sla_report')
        sql = """
            CREATE OR REPLACE VIEW project_sla_report AS (
                SELECT
                    psc.id                               AS id,
                    im.id                                AS document_model_id,
                    ps.name                              AS sla_name,
                    psl.name                             AS sla_line_name,
                    psc.sla_state                        AS sla_state,
                    to_char(psc.sla_start_date, 'YYYY')  AS date_year,
                    to_char(psc.sla_start_date, 'Q')     AS date_quarter,
                    to_char(psc.sla_start_date, 'Month') AS date_month,
                    to_char(psc.sla_start_date, 'WW')    AS date_week,

                    -- Special fields
                    1                                    AS total_count,
                    CASE WHEN psc.sla_state = '1'
                        THEN 1
                        ELSE 0
                    END                                  AS achieved_count,
                    CASE WHEN psc.sla_state IN ('4', '5')
                        THEN 1
                        ELSE 0
                    END                                  AS failed_count,
                    CASE WHEN psc.sla_close_date
                                IS NOT NULL
                        THEN True
                        ELSE False
                    END                                  AS sla_closed
                FROM project_sla_control   AS psc
                LEFT JOIN project_sla_line AS psl
                                            ON psl.id = psc.sla_line_id
                LEFT JOIN project_sla      AS ps
                                            ON ps.id  = psl.sla_id
                LEFT JOIN ir_model         AS im
                                            ON im.model = ps.control_model
            )
        """
        self.env.cr.execute(sql)

