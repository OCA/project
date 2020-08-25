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
        select_str = """
             SELECT
                    (select 1 ) AS nbr,
                    t.id as id,
                    t.date_start as date_start,
                    t.date_end as date_end,
                    t.date_last_stage_update as date_last_stage_update,
                    t.date_deadline as date_deadline,
                    t.user_id,
                    t.project_id,
                    t.priority,
                    t.name as name,
                    t.company_id,
                    t.partner_id,
                    t.stage_id as stage_id,
                    t.kanban_state as state,
                    t.working_days_close as working_days_close,
                    t.working_days_open  as working_days_open,
                    (extract('epoch' from (t.date_deadline-(now() at time zone
                     'UTC'))))/(3600*24)  as delay_endings_days,
                    (t.planned_hours * l.price_unit) as planned_value,
                    (t.planned_hours * s.ev_percent * l.price_unit)
                        as earned_value,
                    (t.effective_hours * e.timesheet_cost) as actual_cost,
                    ((t.planned_hours * l.price_unit) -
                            (t.planned_hours * s.ev_percent * l.price_unit))
                            as schedule_variance,
                    ((t.planned_hours * s.ev_percent * l.price_unit) -
                        (t.effective_hours * e.timesheet_cost) )
                        as cost_variance
        """
        return select_str

    def _from(self):
        return """
            FROM project_task t
        """

    def _join(self):
        return """
            JOIN sale_order_line AS l ON t.sale_line_id = l.id
            JOIN project_task_type AS s ON t.stage_id = s.id
            JOIN hr_employee AS e ON t.user_id = e.user_id
        """

    def _where(self):

        query = """
            WHERE
                t.active = 'true'
        """
        if self._context.get('project_ids'):
            if len(self._context.get('project_ids')) > 1:
                query += """
                    AND
                    t.project_id IN %s
                """ % (str(tuple(self._context.get('project_ids'))))
            else:
                query += """
                    AND
                    t.project_id = %s
                """ % (str(self._context.get('project_ids')[0]))
        return query

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                %s
                %s
                %s
                %s
            )
        """ % (self._table, self._select(), self._from(),
               self._join(), self._where()))
