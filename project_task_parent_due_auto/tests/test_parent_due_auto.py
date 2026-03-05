from dateutil import relativedelta

from odoo import fields

from odoo.addons.base.tests.common import BaseCommon


class AnalyticCommon(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.date_1 = fields.Datetime.today() + relativedelta.relativedelta(days=1)
        cls.date_5 = fields.Datetime.today() + relativedelta.relativedelta(days=5)
        cls.date_7 = fields.Datetime.today() + relativedelta.relativedelta(days=7)
        cls.date_10 = fields.Datetime.today() + relativedelta.relativedelta(days=10)
        cls.test_project = cls.env["project.project"].create(
            {
                "name": "Test Project",
                "privacy_visibility": "employees",
                "alias_name": "project+test",
            }
        )
        cls.task_1 = cls.env["project.task"].create(
            {"name": "Pigs UserTask", "project_id": cls.test_project.id}
        )
        cls.task_2 = cls.env["project.task"].create(
            {"name": "Pigs ManagerTask", "project_id": cls.test_project.id}
        )
        cls.task_3 = cls.env["project.task"].create(
            {
                "name": "Test Task 3",
                "project_id": cls.test_project.id,
            }
        )
        cls.task_2.parent_id = cls.task_1

    def test_setting_parent_due_date_does_not_change_child(self):
        self.task_1.write({"date_deadline": self.date_1})
        self.assertFalse(
            self.task_2.date_deadline,
            "Updating parent deadline should not update child",
        )

    def test_updating_child_due_date_sets_parent(self):
        self.task_2.write({"date_deadline": self.date_5})
        self.assertEqual(
            self.task_1.date_deadline,
            self.date_5,
            "Updating child deadline should update parent date",
        )

    def test_removing_child_due_date_removes_from_parent(self):
        self.task_2.write({"date_deadline": self.date_5})
        self.task_2.date_deadline = False
        self.assertTrue(
            self.task_1.date_deadline,
            "Clearing child should not clear parent",
        )

    def test_closest_due_date_among_children_is_used(self):
        self.task_2.date_deadline = self.date_5
        self.task_3.parent_id = self.task_1
        self.task_3.date_deadline = self.date_10
        self.assertEqual(
            self.task_1.date_deadline,
            self.date_5,
            "Parent deadline should be set to earliest child deadline",
        )

    def test_updating_closest_child_updates_parent(self):
        self.task_2.write({"date_deadline": self.date_5})
        self.task_2.write({"date_deadline": self.date_7})
        self.assertEqual(
            self.task_1.date_deadline,
            self.date_7,
            """Parent deadline should be updated when child changes deadline
            and parent already has a deadline""",
        )

    def test_creating_child_with_due_date_updates_parent(self):
        self.env["project.task"].create(
            {
                "name": "Child Task",
                "project_id": self.test_project.id,
                "parent_id": self.task_1.id,
                "date_deadline": self.date_10,
            }
        )
        self.assertEqual(
            self.task_1.date_deadline,
            self.date_10,
            "Creating child with deadline should update parent",
        )
