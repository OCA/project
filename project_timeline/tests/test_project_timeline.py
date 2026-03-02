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
        cls.project = cls.env["project.project"].create({"name": "Project Test"})
        cls.stage_done = cls.env["project.task.type"].create(
            {
                "name": "Done",
                "fold": True,
            }
        )
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
                "stage_id": self.stage_done.id,
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
        task.stage_id = self.stage_done
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

    def test_uninstall_clean_action(self):
        """Test uninstall hook cleans 'timeline' from view_mode of act_window actions.
        - Case 1: action with multiple view modes: just remove 'timeline'
        - Case 2: action with 'timeline' only: unlink action + related menus
        """
        # Test data
        Action = self.env["ir.actions.act_window"]
        Menu = self.env["ir.ui.menu"]
        action1 = Action.create(
            {
                "name": "Test Action Multi",
                "res_model": "project.task",
                "view_mode": "tree,timeline,form",
            }
        )
        action2 = action1.copy({"view_mode": "timeline"})
        menu2 = Menu.create(
            {
                "name": "Test Menu Solo",
                "action": "ir.actions.act_window,%d" % action2.id,
            }
        )

        # Run the uninstall hook logic
        from ..hooks import _clean_action_view_mode_timeline

        _clean_action_view_mode_timeline(self.env)

        # Case 1: 'timeline' removed, other modes preserved
        self.assertEqual(action1.view_mode, "tree,form")
        # Case 2: action and its menu are deleted
        self.assertFalse(Action.browse(action2.id).exists())
        self.assertFalse(Menu.browse(menu2.id).exists())
