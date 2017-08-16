# -*- coding: utf-8 -*-
# Copyright 2004-2010 Tiny SPRL <http://tiny.be>.
# Copyright 2017 ABF OSIELL <http://osiell.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestProjectGtd(TransactionCase):

    def setUp(self, *args, **kwargs):
        super(TestProjectGtd, self).setUp(*args, **kwargs)
        # Timeboxes
        self.timebox_weekly = self.env.ref("project_gtd.timebox_weekly")
        self.timebox_daily = self.env.ref("project_gtd.timebox_daily")

        # Task
        self.task = self.env.ref("project.project_task_10")

        # Plan
        self.plan = self.create_plan()

    def create_plan(self):
        return self.env['project.timebox.fill.plan'].create({
            'task_ids': [(6, 0, [self.task.id, ])],
            'timebox_id': self.timebox_daily.id,
            'timebox_to_id': self.timebox_weekly.id})

    def test_timebox_weekly(self):
        """
        Check if timebox is weekly after processing the plan.
        """
        self.plan.process()
        self.assertTrue(self.task.timebox_id.id == self.timebox_weekly.id)

    def test_timebox_empty(self):
        """
        Check if timebox is empty after emptiying task.
        """
        context = {
            "active_model": "project.gtd.timebox",
            "active_ids": [self.timebox_weekly.id, ],
            "active_id": self.timebox_weekly.id,
        }
        self.env['project.timebox.empty'].with_context(context)._empty()
        self.assertTrue(self.task.timebox_id != self.timebox_weekly)
