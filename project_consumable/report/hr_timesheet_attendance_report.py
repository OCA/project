# Copyright 2025 - Pierre Verkest
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, tools


class TimesheetAttendance(models.Model):
    _inherit = "hr.timesheet.attendance.report"

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self._cr.execute(
            """CREATE OR REPLACE VIEW %s AS (
            SELECT
                max(id) AS id,
                t.employee_id,
                t.date,
                t.company_id,
                coalesce(sum(t.attendance), 0) AS total_attendance,
                coalesce(sum(t.timesheet), 0) AS total_timesheet,
                coalesce(
                    sum(t.attendance), 0) - coalesce(sum(t.timesheet),
                    0
                ) as total_difference,
                NULLIF(sum(t.timesheet) * t.emp_cost, 0) as timesheets_cost,
                NULLIF(sum(t.attendance) * t.emp_cost, 0) as attendance_cost,
                NULLIF(
                    (coalesce(sum(t.attendance), 0) -  coalesce(sum(t.timesheet), 0))
                     * t.emp_cost,
                    0
                )  as cost_difference
            FROM (
                SELECT
                    -hr_attendance.id AS id,
                    hr_employee.hourly_cost AS emp_cost,
                    hr_attendance.employee_id AS employee_id,
                    hr_attendance.worked_hours AS attendance,
                    NULL AS timesheet,
                    hr_attendance.check_in::date AS date,
                    hr_employee.company_id as company_id
                FROM hr_attendance
                LEFT JOIN hr_employee ON hr_employee.id = hr_attendance.employee_id
            UNION ALL
                SELECT
                    ts.id AS id,
                    hr_employee.hourly_cost AS emp_cost,
                    ts.employee_id AS employee_id,
                    NULL AS attendance,
                    ts.unit_amount AS timesheet,
                    ts.date AS date,
                    ts.company_id AS company_id
                FROM account_analytic_line AS ts
                LEFT JOIN hr_employee ON hr_employee.id = ts.employee_id
                WHERE ts.project_id IS NOT NULL
                    -- change start
                    AND ts.product_id IS NULL
                    -- change end
            ) AS t
            GROUP BY t.employee_id, t.date, t.company_id, t.emp_cost
            ORDER BY t.date
        )
        """
            % self._table
        )
