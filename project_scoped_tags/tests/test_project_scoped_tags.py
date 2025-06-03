from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase, tagged


@tagged("-at_install", "post_install")
class TestProjectScopedTags(TransactionCase):
    def setUp(self):
        super().setUp()

        # Create project manager and normal user
        self.group_manager = self.env.ref("project.group_project_manager")
        self.group_user = self.env.ref("project.group_project_user")
        Users = self.env["res.users"].with_context(no_reset_password=True)

        self.manager = Users.create(
            {
                "name": "Manager",
                "login": "manager_tags",
                "email": "manager_tags@example.com",
                "groups_id": [
                    (6, 0, [self.group_manager.id, self.env.ref("base.group_user").id])
                ],
            }
        )
        self.user = Users.create(
            {
                "name": "Normal User",
                "login": "user_tags",
                "email": "user_tags@example.com",
                "groups_id": [
                    (6, 0, [self.group_user.id, self.env.ref("base.group_user").id])
                ],
            }
        )

        # Create two projects
        self.project1 = self.env["project.project"].create({"name": "Project 1"})
        self.project2 = self.env["project.project"].create({"name": "Project 2"})

        # Create three tags
        self.tag1 = self.env["project.tags"].create({"name": "Tag Global"})
        self.tag2 = self.env["project.tags"].create(
            {"name": "Tag P1", "available_in_project_ids": [(6, 0, [self.project1.id])]}
        )
        self.tag3 = self.env["project.tags"].create(
            {"name": "Tag P2", "available_in_project_ids": [(6, 0, [self.project2.id])]}
        )

        # Create tasks for each project
        self.task1 = self.env["project.task"].create(
            {
                "name": "Task1 P1",
                "project_id": self.project1.id,
                "tag_ids": [(6, 0, [self.tag1.id])],
            }
        )
        self.task2 = self.env["project.task"].create(
            {
                "name": "Task 1 P2",
                "project_id": self.project2.id,
                "tag_ids": [(6, 0, [self.tag2.id, self.tag3.id])],
            }
        )

    def test_tag_global_availability(self):
        # Tag1 has no project, so it should be global
        self.assertTrue(self.tag1.globally_available)
        # Tag2 and Tag3 are not global
        self.assertFalse(self.tag2.globally_available)
        self.assertFalse(self.tag3.globally_available)

    def test_tag_assignment_and_filtering(self):
        # Only global tags and tags allowed for project1 should be available for project1
        tags_project1 = self.env["project.tags"].search(
            [
                "|",
                ("globally_available", "=", True),
                ("available_in_project_ids", "in", [self.project1.id]),
            ]
        )
        tag_names1 = set(tags_project1.mapped("name"))
        self.assertIn("Tag Global", tag_names1)  # global
        self.assertIn("Tag P1", tag_names1)  # allowed for project1
        self.assertNotIn("Tag P2", tag_names1)  # only project2

        # Only global tags and tags allowed for project2 should be available for project2
        tags_project2 = self.env["project.tags"].search(
            [
                "|",
                ("globally_available", "=", True),
                ("available_in_project_ids", "in", [self.project2.id]),
            ]
        )
        tag_names2 = set(tags_project2.mapped("name"))
        self.assertIn("Tag Global", tag_names2)  # global
        self.assertNotIn("Tag P1", tag_names2)  # only project1
        self.assertIn("Tag P2", tag_names2)  # allowed for project2

    def test_tag_uniqueness_on_create(self):
        # Creating a tag with an existing name returns the existing tag
        tag_dup = self.env["project.tags"].create({"name": "Tag Global"})
        self.assertEqual(tag_dup.id, self.tag1.id)
        self.assertEqual(tag_dup.name, self.tag1.name)

    def test_tag_assignment_on_task(self):
        # Assign tag2 (not global, only project1) to a task of project2 should not
        # be allowed in the UI, but in ORM it works unless protected
        self.task2.tag_ids = [(4, self.tag2.id)]
        self.assertIn(self.tag2, self.task2.tag_ids)
        # Now tag2 should also be available for project2 (simulate domain logic)
        self.tag2.available_in_project_ids = [(4, self.project2.id)]
        tags_project2 = self.env["project.tags"].search(
            [
                "|",
                ("globally_available", "=", True),
                ("available_in_project_ids", "in", [self.project2.id]),
            ]
        )
        self.assertIn(self.tag2, tags_project2)

    def test_available_in_project_ids_update(self):
        # Add project2 to tag2 available_in_project_ids
        self.tag2.available_in_project_ids = [(4, self.project2.id)]
        self.assertIn(self.project2, self.tag2.available_in_project_ids)
        # Remove project1 from tag2
        self.tag2.available_in_project_ids = [(3, self.project1.id)]
        self.assertNotIn(self.project1, self.tag2.available_in_project_ids)
        # Now only project2 has tag2
        self.assertEqual(
            set(self.tag2.available_in_project_ids.ids), {self.project2.id}
        )

    def test_tag_global_toggle(self):
        # Remove all projects: tag2 becomes global
        self.tag2.available_in_project_ids = [(5, 0, 0)]
        self.assertTrue(self.tag2.globally_available)
        # Only project managers can do that (simulate by removing from user)
        self.tag2.available_in_project_ids = [(4, self.project1.id)]
        with self.assertRaises(AccessError):
            self.tag2.with_user(self.user).write(
                {"available_in_project_ids": [(5, 0, 0)]}
            )

    def test_view_filtering(self):
        # Simulate tag filtering in search view
        domain = [
            "|",
            ("globally_available", "=", True),
            ("available_in_project_ids", "in", [self.project1.id]),
        ]
        tags = self.env["project.tags"].search(domain)
        for tag in tags:
            self.assertTrue(
                tag.globally_available or self.project1 in tag.available_in_project_ids
            )

    def test_only_manager_can_edit_available_in_project_ids(self):
        # Try to edit available_in_project_ids as normal user
        with self.assertRaises(AccessError):
            self.tag2.with_user(self.user).write(
                {"available_in_project_ids": [(4, self.project2.id)]}
            )
        # Project manager can
        self.tag2.with_user(self.manager).write(
            {"available_in_project_ids": [(4, self.project2.id)]}
        )
        self.assertIn(self.project2, self.tag2.available_in_project_ids)
