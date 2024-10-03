# Copyright 2018 Onestein
# Copyright 2024 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests.common import TransactionCase


class TestProjectTimeline(TransactionCase):
    def test_01_flow_filling(self):
        task = self.env["project.task"].create({"name": "1"})
        self.assertFalse(task.planned_date_start)
        task.user_ids = self.env.user
        self.assertTrue(task.planned_date_start)
        self.assertFalse(task.planned_date_end)
        task.stage_id = self.ref("project.project_stage_2")
        self.assertTrue(task.planned_date_end)

    def test_02_no_filling(self):
        stage_id = self.ref("project.project_stage_2")
        task = self.env["project.task"].create(
            {
                "name": "1",
                "planned_date_start": "2018-05-01 00:00:00",
                "planned_date_end": "2018-05-07 00:00:00",
            }
        )
        task.user_ids = self.env.user
        self.assertEqual(
            task.planned_date_start, fields.Datetime.from_string("2018-05-01")
        )
        task.stage_id = stage_id
        self.assertEqual(
            task.planned_date_end, fields.Datetime.from_string("2018-05-07")
        )
