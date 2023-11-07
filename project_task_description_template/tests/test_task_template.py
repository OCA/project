# Copyright (C) 2023 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo.tests import common


class TestTaskTemplate(common.TransactionCase):
    def setUp(self):
        super().setUp()
        # create tag model
        tag_model = self.env["project.tags"]
        # creating tags: Red, Green, Blue, White, Yellow
        self.tag_red = tag_model.create({"name": "Red"})
        self.tag_green = tag_model.create({"name": "Green"})
        self.tag_blue = tag_model.create({"name": "Blue"})
        self.tag_white = tag_model.create({"name": "White"})
        self.tag_yellow = tag_model.create({"name": "Yellow"})
        # create res users model
        res_users_model = self.env["res.users"]
        # create users: Bob, Mike, Kate
        self.user_bob = res_users_model.create(
            {"name": "Bob", "email": "bob@example.com", "login": "bob"}
        )
        self.user_mike = res_users_model.create(
            {"name": "Mike", "email": "mike@example.com", "login": "mike"}
        )
        self.user_kate = res_users_model.create(
            {"name": "Kate", "email": "kate@example.com", "login": "kate"}
        )
        # create task template model
        task_template_model = self.env["project.task.template"]
        # create task templates:

        self.template_1 = task_template_model.create(
            {
                "name": "Template1",
                "tag_ids": [
                    self.tag_red.id,
                    self.tag_green.id,
                ],
                "user_id": self.user_bob.id,
                "description": "This is template 1",
            }
        )
        self.template_2 = task_template_model.create(
            {
                "name": "Template2",
                "tag_ids": [
                    self.tag_blue.id,
                    self.tag_white.id,
                ],
                "user_id": self.user_mike.id,
                "description": "This is template 2",
            }
        )
        # create project model
        project_model = self.env["project.project"]
        # create projects : "Project 1" and add templates 1-2
        self.project_1 = project_model.create(
            {
                "name": "Project 1",
                "task_template_ids": [self.template_1.id, self.template_2.id],
            }
        )
        # create task model
        project_task_model = self.env["project.task"]
        self.test_task_1 = project_task_model.create(
            {
                "name": "Test task 1",
                "user_id": self.user_kate.id,
                "tag_ids": [
                    self.tag_yellow.id,
                ],
                "description": "This is task1",
                "task_template_id": False,
            }
        )

    def test_task_1_template_1(self):
        self.test_task_1.task_template_id = self.template_1.id
        self.test_task_1._onchange_task_template_id()
        self.assertEqual(self.test_task_1.user_id.id, self.template_1.user_id.id)
        self.assertEqual(self.test_task_1.tag_ids.ids, self.template_1.tag_ids.ids)
        self.assertEqual(self.test_task_1.description, self.template_1.description)

    def test_task_1_template_2(self):
        self.test_task_1.task_template_id = self.template_2.id
        self.test_task_1._onchange_task_template_id()
        self.assertEqual(self.test_task_1.user_id.id, self.template_2.user_id.id)
        self.assertEqual(self.test_task_1.tag_ids.ids, self.template_2.tag_ids.ids)
        self.assertEqual(self.test_task_1.description, self.template_2.description)

    def test_task_1_template_false(self):
        self.test_task_1.task_template_id = self.template_2.id
        self.test_task_1._onchange_task_template_id()
        self.test_task_1.task_template_id = False
        self.test_task_1._onchange_task_template_id()
        self.assertEqual(self.test_task_1.user_id.id, self.template_2.user_id.id)
        self.assertEqual(self.test_task_1.tag_ids.ids, self.template_2.tag_ids.ids)
        self.assertEqual(self.test_task_1.description, self.template_2.description)
