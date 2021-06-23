# Copyright 2004-2010 Tiny SPRL <http://tiny.be>.
# Copyright 2017 ABF OSIELL <http://osiell.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestProjectGtd(TransactionCase):
    def setUp(self):
        super().setUp()

        self.project_timebox_empty = self.env["project.timebox.empty"]

        # Timeboxes
        self.timebox_weekly = self.env.ref("project_gtd.timebox_weekly")
        self.timebox_daily = self.env.ref("project_gtd.timebox_daily")

        # Task
        self.task = self.env.ref("project.project_task_10")

        # Plan
        self.plan = self.create_plan()

    def create_plan(self):
        return self.env["project.timebox.fill.plan"].create(
            {
                "task_ids": [
                    (
                        6,
                        0,
                        [
                            self.task.id,
                        ],
                    )
                ],
                "timebox_id": self.timebox_daily.id,
                "timebox_to_id": self.timebox_weekly.id,
            }
        )

    def test_timebox_weekly(self):
        """
        Check if timebox is weekly after processing the plan.
        """
        self.plan.process()
        self.assertTrue(self.task.timebox_id.id == self.timebox_weekly.id)

    def test_timebox_empty_close(self):
        """
        Check if timebox is empty after emptiying task.
        """
        self.process()
        self.assertFalse(self.task.timebox_id)

    def test_timebox_empty_up(self):
        """
        Check correct timebox after emptiying task.
        """
        self.task.user_id = self.env.uid
        self.process()
        self.assertTrue(self.task.timebox_id == self.timebox_daily)

    def process(self):
        self.plan.process()
        context = {
            "active_model": "project.gtd.timebox",
            "active_ids": [
                self.timebox_weekly.id,
            ],
            "active_id": self.timebox_weekly.id,
        }
        self.project_timebox_empty.with_context(context).process()
