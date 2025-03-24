# Copyright 2024 Tecnativa - Carolina Fernandez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from freezegun import freeze_time

from odoo.addons.base.tests.common import BaseCommon


class TestProject(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.project = cls.env["project.project"].create({"name": "Test Project"})
        cls.stage = cls.env["project.project.stage"].create({"name": "Test Stage"})

    @freeze_time("2024-08-19 08:00")
    def test_project_stage_last_update_date(self):
        self.assertEqual(self.project.stage_last_update_date, False)
        self.project.write({"stage_id": self.stage.id})
        self.assertEqual(
            self.project.stage_last_update_date.strftime("%Y-%m-%d %H:%M"),
            "2024-08-19 08:00",
        )
