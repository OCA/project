from datetime import date, datetime

from pytz import utc

from . import base


class TestResourceCalendar(base.BaseCase):
    # This is necesary to test like this to increment
    # test coverage, because it's not posible in code
    # to get this states

    def test_get_working_days_of_date_no_date_start(self):
        company = self.env.user.company_id
        calendar = self.env["resource.calendar"].search(
            [("company_id", "=", company.id)], limit=1
        )
        resource = self.env["resource.resource"].search(
            [("user_id", "=", self.env.user.id)], limit=1
        )
        # start_dt < end_dt
        days = calendar.get_working_days_of_date(
            start_dt=utc.localize(datetime(2023, 7, 10)),
            end_dt=utc.localize(datetime(2023, 7, 11)),
            resource=resource,
        )
        self.assertEqual(days, 1)

        # start_dt > end_dt
        days = calendar.get_working_days_of_date(
            start_dt=utc.localize(datetime(2023, 7, 10)),
            end_dt=utc.localize(datetime(2023, 7, 1)),
            resource=resource,
        )
        self.assertEqual(days, 0)

        # No end_dt
        days = calendar.get_working_days_of_date(
            start_dt=utc.localize(datetime(2023, 7, 10)), resource=resource,
        )
        self.assertTrue(days > 0)

        # No start_dt and end_dt
        days = calendar.get_working_days_of_date(resource=resource,)
        self.assertEqual(days, 0)

        # No start_dt
        days = calendar.get_working_days_of_date(
            end_dt=utc.localize(datetime(2023, 7, 10)), resource=resource,
        )
        self.assertEqual(days, 0)

        # No resource
        days = calendar.get_working_days_of_date(
            start_dt=utc.localize(datetime(2023, 7, 10)),
            end_dt=utc.localize(datetime(2023, 7, 11)),
        )
        self.assertEqual(days, 1)

    def test_plan_days_to_resource(self):
        company = self.env.user.company_id
        calendar = self.env["resource.calendar"].search(
            [("company_id", "=", company.id)], limit=1
        )
        project = self.project_create(
            self.num_tasks,
            {
                "calculation_type": self.calculation_type,
                "name": "Test project",
                "date_start": date(2015, 8, 1),
                "date": date(2015, 8, 31),
                "resource_calendar_id": False,
            },
        )

        task = project.tasks[0]

        # No compute_leaves
        planned_dt = calendar.plan_days_to_resource(0, task.date_start)
        self.assertEqual(task.date_start, planned_dt)

        # From days = 0
        planned_dt = calendar.plan_days_to_resource(
            0, task.date_start, compute_leaves=True
        )
        self.assertEqual(task.date_start, planned_dt)
