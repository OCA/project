# Copyright 2018 Onestein
# Copyright 2024 Tecnativa - Pedro M. Baeza
# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import exceptions, fields

from odoo.addons.base.tests.common import BaseCommon


class TestProjectTimeline(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.project = cls.env.ref("project.project_project_1")
        cls.stage = cls.env.ref("project.project_stage_2")
        cls.task = cls.env["project.task"].create(
            {"name": "test", "user_ids": False, "project_id": cls.project.id}
        )

    def test_01_flow_filling(self):
        self.assertFalse(self.task.planned_date_start)
        self.task.user_ids = self.env.user
        self.assertTrue(self.task.planned_date_start)
        self.assertFalse(self.task.planned_date_end)
        self.task.write(
            {
                "stage_id": self.stage.id,
                "date_end": fields.Datetime.add(self.task.planned_date_start, days=1),
            }
        )
        self.assertTrue(self.task.planned_date_end)

    def test_02_no_filling(self):
        task = self.env["project.task"].create(
            {
                "name": "1",
                "planned_date_start": "2018-05-01 00:00:00",
                "planned_date_end": "2018-05-07 00:00:00",
                "project_id": self.project.id,
            }
        )
        task.user_ids = self.env.user
        self.assertEqual(
            task.planned_date_start, fields.Datetime.from_string("2018-05-01")
        )
        task.stage_id = self.stage
        self.assertEqual(
            task.planned_date_end, fields.Datetime.from_string("2018-05-07")
        )

    def test_misc_dates(self):
        self.assertFalse(self.task.planned_date_start)
        self.assertFalse(self.task.date_end)

    def test_valid_dates(self):
        self.task.planned_date_start = fields.Datetime.today()
        self.task.date_end = fields.Datetime.add(self.task.planned_date_start, days=1)
        self.assertGreater(self.task.date_end, self.task.planned_date_start)

    def test_invalid_dates(self):
        self.task.write({"user_ids": self.env.user.ids})
        with self.assertRaises(exceptions.ValidationError):
            self.task.planned_date_end = fields.Datetime.subtract(
                self.task.planned_date_start, days=1
            )
