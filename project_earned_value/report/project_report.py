# Copyright (C) 2020 Open Source Integrators
# Copyright (C) 2020 Serpent Consulting Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, tools


class ReportProjectTaskUser(models.Model):
    _inherit = "report.project.task.user"

    planned_value = fields.Float('Planned Value', readonly=True)
    earned_value = fields.Float('Earned Value', readonly=True)
    actual_cost = fields.Float('Actual Cost', readonly=True)
    schedule_variance = fields.Float('Schedule Variance', readonly=True)
    cost_variance = fields.Float('Cost Variance', readonly=True)

    def _select(self):
        select_str = super()._select()
        select_str += """,
                    (COALESCE(COALESCE(t.planned_hours, 0), 0) *
                    COALESCE(COALESCE(l.price_unit, 0), 0)) as planned_value,
                    (COALESCE(COALESCE(t.planned_hours, 0), 0) *
                    COALESCE(COALESCE(s.ev_percent, 0), 0) *
                    COALESCE(COALESCE(l.price_unit, 0), 0))
                        as earned_value,
                    (COALESCE(t.effective_hours, 0) *
                    COALESCE(e.timesheet_cost, 0)) as actual_cost,
                    ((COALESCE(t.planned_hours, 0) *
                    COALESCE(l.price_unit, 0)) -
                            (COALESCE(t.planned_hours, 0) *
                            COALESCE(s.ev_percent, 0) *
                            COALESCE(l.price_unit, 0)))
                            as schedule_variance,
                    ((COALESCE(t.planned_hours, 0) *
                    COALESCE(s.ev_percent, 0) *
                    COALESCE(l.price_unit, 0)) -
                        (COALESCE(t.effective_hours, 0) *
                        COALESCE(e.timesheet_cost, 0)) )
                        as cost_variance
        """
        return select_str

    def _from(self):
        return """
            FROM project_task t
            LEFT OUTER JOIN sale_order_line AS l ON t.sale_line_id = l.id
            LEFT OUTER JOIN project_task_type AS s ON t.stage_id = s.id
            LEFT OUTER JOIN hr_employee AS e ON t.user_id = e.user_id
        """

    def _where(self):

        query = """
            WHERE
                t.active = 'true'
        """
        return query

    def _group_by(self):
        group_by_str = super()._group_by()
        group_by_str += """
                    ,COALESCE(l.price_unit, 0),
                    COALESCE(s.ev_percent, 0),
                    COALESCE(e.timesheet_cost, 0)
        """
        return group_by_str

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                %s
                %s
                %s
            )
        """ % (self._table, self._select(), self._from(),
               self._where()))
