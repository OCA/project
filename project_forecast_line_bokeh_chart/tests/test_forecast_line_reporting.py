# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import date, timedelta

from odoo.tests import TransactionCase, tagged


@tagged("-at_install", "post_install")
class TestForecastLineReporting(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env["hr.employee"].create({"name": "Test Employee"})
        cls.project = cls.env["project.project"].create({"name": "Test Project"})
        cls.role = cls.env["forecast.role"].create({"name": "Test Role"})
        # spread over more than one week and one month, so the week/month
        # granularities actually have more than a single bucket to align
        cls.start = date.today()
        for offset in range(0, 45, 3):
            day = cls.start + timedelta(days=offset)
            cls.env["forecast.line"].create(
                {
                    "company_id": cls.env.company.id,
                    "type": "forecast",
                    "forecast_role_id": cls.role.id,
                    "employee_id": cls.employee.id,
                    "project_id": cls.project.id,
                    "date_from": day,
                    "date_to": day,
                    # forecast_hours, not consolidated_forecast: the latter
                    # is a stored computed field and any value written to it
                    # directly gets silently overwritten by the compute
                    "forecast_hours": -8.0,
                    "res_model": "project.task",
                    "res_id": 0,
                    "name": "Test forecast line",
                }
            )
        # a line with no employee: this is what actually reaches the
        # groupby loop when the wizard has no employee_ids/project_ids
        # filter (that domain is ("employee_id", "=", False)), which is
        # the exact zero-input path that used to crash
        cls.env["forecast.line"].create(
            {
                "company_id": cls.env.company.id,
                "type": "forecast",
                "forecast_role_id": cls.role.id,
                "project_id": cls.project.id,
                "date_from": cls.start,
                "date_to": cls.start,
                "forecast_hours": -8.0,
                "res_model": "project.task",
                "res_id": 0,
                "name": "Test unassigned forecast line",
            }
        )

    def _make_wizard(self, granularity, **values):
        return self.env["forecast.line.reporting"].create(
            {"granularity": granularity, **values}
        )

    def test_prepare_bokeh_chart_data_all_granularities(self):
        # regression test for a KeyError on `__range` caused by the 19.0
        # migration to read_group's new date groupby key format, and for the
        # x-axis dates not lining up with the group dates for week/month
        # (week groups are anchored on the language's first day of the
        # week, not the ISO/Monday convention)
        for granularity in ("day", "week", "month"):
            wizard = self._make_wizard(
                granularity, employee_ids=[(6, 0, self.employee.ids)]
            )
            employees, projects, data_project, __ = wizard._prepare_bokeh_chart_data()
            self.assertIn(self.employee.name, employees)
            self.assertIn(self.project.name, projects)
            forecast_by_date = data_project[self.employee.name][self.project.name]
            dates = wizard._get_time_range()
            plotted = [forecast_by_date.get(d, 0) for d in dates]
            # every forecast must land on one of the x-axis dates: a
            # mismatch here means bars would silently render empty
            self.assertEqual(sum(plotted), sum(forecast_by_date.values()))
            self.assertTrue(any(plotted))

    def test_bokeh_chart_computes_on_multi_record(self):
        # regression test: _compute_bokeh_chart used to read self.date_from
        # directly, raising on a multi-record recordset
        wizards = self._make_wizard(
            "day", employee_ids=[(6, 0, self.employee.ids)]
        ) | self._make_wizard("month", employee_ids=[(6, 0, self.employee.ids)])
        self.assertTrue(all(wizards.mapped("bokeh_chart")))

    def test_bokeh_chart_no_filter(self):
        # this is the exact zero-input case that used to raise
        # KeyError: 'date_from' as soon as any forecast.line existed: the
        # wizard's domain then is ("employee_id", "=", False), which the
        # unassigned line from setUpClass matches, actually reaching the
        # groupby loop instead of returning early on an empty result
        not_assigned = self.env._("Not assigned to an employee")
        for granularity in ("day", "week", "month"):
            wizard = self._make_wizard(granularity)
            employees, __, data_project, __ = wizard._prepare_bokeh_chart_data()
            self.assertIn(not_assigned, employees)
            self.assertTrue(wizard.bokeh_chart)
