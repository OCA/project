from odoo import Command
from odoo.exceptions import AccessError

from odoo.addons.base.tests.common import BaseCommon


class TestProjectReadonly(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group_user = cls.env.ref("base.group_user")
        cls.group_project_user = cls.env.ref("project.group_project_user")
        cls.group_readonly = cls.env.ref("project_readonly.group_project_readonly")

        cls.partner = cls.env["res.partner"].create({"name": "Test Customer"})

        cls.user_owner = cls.env["res.users"].create(
            {
                "name": "Project Owner",
                "login": "project_readonly_owner",
                "group_ids": [
                    Command.link(cls.group_user.id),
                    Command.link(cls.group_project_user.id),
                ],
            }
        )
        cls.project = cls.env["project.project"].create(
            {
                "name": "Test Project",
                "partner_id": cls.partner.id,
                "user_id": cls.user_owner.id,
                "privacy_visibility": "employees",
            }
        )
        cls.task = cls.env["project.task"].create(
            {
                "name": "Test Task",
                "project_id": cls.project.id,
                "user_ids": [Command.link(cls.user_owner.id)],
            }
        )
        cls.restricted_project = cls.env["project.project"].create(
            {
                "name": "Test Restricted Project",
                "partner_id": cls.partner.id,
                "user_id": cls.user_owner.id,
                "privacy_visibility": "followers",
            }
        )
        cls.restricted_task = cls.env["project.task"].create(
            {
                "name": "Test Restricted Task",
                "project_id": cls.restricted_project.id,
            }
        )

        cls.user_employee = cls.env["res.users"].create(
            {
                "name": "Plain Employee",
                "login": "project_readonly_employee",
                "group_ids": [Command.link(cls.group_user.id)],
            }
        )
        cls.user_readonly = cls.env["res.users"].create(
            {
                "name": "Project Readonly",
                "login": "project_readonly_user",
                "group_ids": [
                    Command.link(cls.group_user.id),
                    Command.link(cls.group_readonly.id),
                ],
            }
        )
        cls.user_project_user = cls.env["res.users"].create(
            {
                "name": "Project User",
                "login": "project_readonly_project_user",
                "group_ids": [
                    Command.link(cls.group_user.id),
                    Command.link(cls.group_project_user.id),
                ],
            }
        )
        cls.user_project_user_readonly = cls.env["res.users"].create(
            {
                "name": "Project User Readonly",
                "login": "project_readonly_project_user_readonly",
                "group_ids": [
                    Command.link(cls.group_user.id),
                    Command.link(cls.group_project_user.id),
                    Command.link(cls.group_readonly.id),
                ],
            }
        )

    def test_readonly_user_can_read_project(self):
        project = self.project.with_user(self.user_readonly)
        self.assertTrue(project.read(["name", "task_count"]))
        self.assertTrue(project.task_ids.read(["name"]))

    def test_readonly_user_can_read_restricted_project(self):
        self.assertTrue(
            self.restricted_project.with_user(self.user_readonly).read(["name"])
        )
        self.assertTrue(
            self.restricted_task.with_user(self.user_readonly).read(["name"])
        )

    def test_readonly_user_can_read_task_report(self):
        self.assertTrue(
            self.env["report.project.task.user"]
            .with_user(self.user_readonly)
            .search_count([])
        )

    def test_employee_without_group_cannot_read_restricted_project(self):
        with self.assertRaises(AccessError):
            self.restricted_project.with_user(self.user_employee).read(["name"])

    def test_readonly_user_cannot_create_project(self):
        with self.assertRaises(AccessError):
            self.env["project.project"].with_user(self.user_readonly).create(
                {"name": "Nope"}
            )

    def test_readonly_user_cannot_write_project(self):
        with self.assertRaises(AccessError):
            self.project.with_user(self.user_readonly).write({"name": "touched"})

    def test_readonly_user_cannot_unlink_project(self):
        with self.assertRaises(AccessError):
            self.project.with_user(self.user_readonly).unlink()

    def test_readonly_user_cannot_create_task(self):
        with self.assertRaises(AccessError):
            self.env["project.task"].with_user(self.user_readonly).create(
                {"name": "Nope", "project_id": self.project.id}
            )

    def test_readonly_user_cannot_write_task(self):
        with self.assertRaises(AccessError):
            self.task.with_user(self.user_readonly).write({"name": "touched"})

    def test_readonly_user_cannot_unlink_task(self):
        with self.assertRaises(AccessError):
            self.task.with_user(self.user_readonly).unlink()

    def test_project_user_with_readonly_group_reads_restricted_project(self):
        self.assertTrue(
            self.restricted_project.with_user(self.user_project_user_readonly).read(
                ["name"]
            )
        )

    def test_project_user_without_readonly_group_cannot_read_restricted_project(
        self,
    ):
        with self.assertRaises(AccessError):
            self.restricted_project.with_user(self.user_project_user).read(["name"])

    def test_menus_visible_for_readonly_user(self):
        visible = (
            self.env["ir.ui.menu"]
            .with_user(self.user_readonly)
            .search([])
            ._filter_visible_menus()
        )
        for xmlid in (
            "project.menu_main_pm",
            "project.menu_projects",
            "project.menu_project_management_my_tasks",
            "project.menu_project_management_all_tasks",
            "project.menu_project_report_task_analysis",
        ):
            self.assertIn(self.env.ref(xmlid).id, visible.ids)

    def test_root_menu_not_visible_for_plain_employee(self):
        visible = (
            self.env["ir.ui.menu"]
            .with_user(self.user_employee)
            .search([])
            ._filter_visible_menus()
        )
        self.assertNotIn(self.env.ref("project.menu_main_pm").id, visible.ids)
