# Copyright 2024 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import ast
import json

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestProjectRequiredFieldByStage(TransactionCase):
    def setUp(self):
        super().setUp()

        self.project_project_model = self.env["project.project"]
        self.project_task_type_model = self.env["project.task.type"]
        self.project_task_model = self.env["project.task"]
        self.res_users_model = self.env["res.users"]
        self.project_project_1 = self.project_project_model.create(
            {
                "name": "Project 1",
            }
        )
        self.project_task_type_1 = self.project_task_type_model.create(
            {
                "name": "Project Stage 1",
                "project_ids": [(4, self.project_project_1.id)],
            }
        )
        self.project_task_type_2 = self.project_task_type_model.create(
            {
                "name": "Project Stage 2",
                "required_field_ids": [
                    # integer
                    (
                        4,
                        self.env.ref("project.field_project_task__planned_hours").id,
                    ),
                    # M2O
                    (
                        4,
                        self.env.ref("project.field_project_task__project_id").id,
                    ),
                    # M2M
                    (
                        4,
                        self.env.ref("project.field_project_task__user_ids").id,
                    ),
                    # bool
                    (
                        4,
                        self.env.ref("project.field_project_task__active").id,
                    ),
                ],
                "project_ids": [(4, self.project_project_1.id)],
            }
        )

        self.project_task_1 = self.project_task_model.create(
            {
                "name": "Project Task 1",
                "project_id": self.project_project_1.id,
                "user_ids": False,
                "planned_hours": 12,
                "stage_id": self.project_task_type_1.id,
                "active": True,
            }
        )
        self.res_users_1 = self.res_users_model.create(
            {
                "name": "User 1",
                "login": "user@example.com",
                "email": "user@example.com",
                "active": True,
            }
        )

    def test_locking(self):
        with self.assertRaises(UserError):
            self.project_task_1.write(
                {
                    "stage_id": self.project_task_type_2.id,
                }
            )
        self.project_task_1.write(
            {
                "user_ids": [(4, self.res_users_1.id)],
            }
        )
        self.project_task_1.write(
            {
                "stage_id": self.project_task_type_2.id,
            }
        )
        self.assertEqual(self.project_task_1.stage_id.id, self.project_task_type_2.id)

    def test_get_view_required_fields(self):
        arch, view = self.project_task_1._get_view(view_type="form")
        # default  will be project.task_form_view2
        node = arch.xpath("//field[@name='user_ids']")
        self.assertTrue(node)
        attrs = ast.literal_eval(node[0].attrib.get("attrs", "{}"))
        self.assertIn("required", attrs)
        self.assertIn(self.project_task_type_2.id, attrs["required"][0][2])
        # to cover all logical branches we need a view that has fields with an attrs
        # without "required" and another with an attrs with "required", user_id has
        # no attrs in view.
        self.project_task_type_2.write(
            {
                "required_field_ids": [
                    (4, self.env.ref("project.field_project_task__repeat_interval").id),
                    (
                        4,
                        self.env.ref(
                            "project.field_project_task__personal_stage_type_id"
                        ).id,
                    ),
                ],
            }
        )
        arch, view = self.project_task_1._get_view(view_type="form")
        # repeat_interval has attrs with required, we verify injection after '|' operator
        node2 = arch.xpath("//field[@name='repeat_interval']")
        self.assertTrue(node2)
        attrs2 = json.loads(node2[0].attrib.get("attrs", "{}"))
        self.assertIn("required", attrs2)
        self.assertEqual("|", attrs2["required"][0])
        self.assertIn(self.project_task_type_2.id, attrs2["required"][2][2])
        # personal_stage_type_id has attrs with no required, we verify injection
        node3 = arch.xpath("//field[@name='personal_stage_type_id']")
        self.assertTrue(node3)
        attrs3 = json.loads(node3[0].attrib.get("attrs", "{}"))
        self.assertIn("required", attrs3)
        self.assertIn(self.project_task_type_2.id, attrs3["required"][0][2])
        # integer field check
        node4 = arch.xpath("//field[@name='planned_hours']")
        self.assertTrue(node4)
        attrs4 = json.loads(node4[0].attrib.get("attrs", "{}"))
        self.assertIn("required", attrs4)
        self.assertIn(self.project_task_type_2.id, attrs3["required"][0][2])
        # m2o field check
        node5 = arch.xpath("//field[@name='project_id']")
        self.assertTrue(node5)
        attrs5 = json.loads(node5[0].attrib.get("attrs", "{}"))
        self.assertIn("required", attrs5)
        self.assertIn(self.project_task_type_2.id, attrs3["required"][0][2])
