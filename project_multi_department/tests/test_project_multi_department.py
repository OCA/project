# Copyright 2026 INVITU (<https://www.invitu.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase, new_test_user


class TestProjectMultiDepartment(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.dept_a, cls.dept_b = cls.env["hr.department"].create(
            [{"name": "Department A"}, {"name": "Department B"}]
        )
        groups = "base.group_user,project.group_project_user"
        cls.user_a = new_test_user(cls.env, "pmd_user_a", groups=groups)
        cls.user_b = new_test_user(cls.env, "pmd_user_b", groups=groups)
        cls.env["hr.employee"].create(
            [
                {
                    "name": "Employee A",
                    "user_id": cls.user_a.id,
                    "department_id": cls.dept_a.id,
                },
                {
                    "name": "Employee B",
                    "user_id": cls.user_b.id,
                    "department_id": cls.dept_b.id,
                },
            ]
        )
        Project = cls.env["project.project"]
        cls.project_internal = Project.create(
            {
                "name": "Internal",
                "privacy_visibility": "employees",
                "department_ids": [(6, 0, cls.dept_a.ids)],
            }
        )
        cls.project_portal = Project.create(
            {
                "name": "Portal",
                "privacy_visibility": "portal",
                "department_ids": [(6, 0, cls.dept_a.ids)],
            }
        )
        cls.project_no_dept = Project.create(
            {
                "name": "No department",
                "privacy_visibility": "employees",
                "department_ids": [(5,)],
            }
        )
        cls.task_internal = cls.env["project.task"].create(
            {"name": "Task", "project_id": cls.project_internal.id}
        )

    def _visible(self, user, records):
        return records.with_user(user).search([("id", "in", records.ids)])

    def test_department_member(self):
        projects = self.project_internal | self.project_portal
        self.assertEqual(self._visible(self.user_a, projects), projects)
        self.assertEqual(
            self._visible(self.user_a, self.task_internal), self.task_internal
        )

    def test_not_department_member(self):
        projects = self.project_internal | self.project_portal
        self.assertFalse(self._visible(self.user_b, projects))
        self.assertFalse(self._visible(self.user_b, self.task_internal))

    def test_project_without_department(self):
        self.assertEqual(
            self._visible(self.user_b, self.project_no_dept), self.project_no_dept
        )

    def test_private_project_follower(self):
        self.project_internal.privacy_visibility = "followers"
        self.project_internal.message_subscribe(partner_ids=self.user_b.partner_id.ids)
        self.assertEqual(
            self._visible(self.user_b, self.project_internal), self.project_internal
        )

    def test_portal_user(self):
        portal = new_test_user(self.env, "pmd_portal", groups="base.group_portal")
        task = self.env["project.task"].create(
            {"name": "Portal task", "project_id": self.project_portal.id}
        )
        projects = self.project_portal | self.project_internal
        self.assertFalse(self._visible(portal, projects))
        self.assertFalse(self._visible(portal, task))
        projects.message_subscribe(partner_ids=portal.partner_id.ids)
        task.message_subscribe(partner_ids=portal.partner_id.ids)
        self.assertEqual(self._visible(portal, projects), self.project_portal)
        self.assertEqual(self._visible(portal, task), task)

    def test_project_manager(self):
        self.project_internal.user_id = self.user_b
        self.assertEqual(
            self._visible(self.user_b, self.project_internal), self.project_internal
        )

    def test_task_assignee(self):
        self.task_internal.user_ids = self.user_b
        self.assertEqual(
            self._visible(self.user_b, self.task_internal), self.task_internal
        )
        self.assertFalse(self._visible(self.user_b, self.project_internal))

    def test_project_administrator(self):
        admin = new_test_user(
            self.env,
            "pmd_admin",
            groups="base.group_user,project.group_project_manager",
        )
        self.assertFalse(self._visible(admin, self.project_internal))
