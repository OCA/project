# Copyright 2016 Tecnativa <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import odoo.tests.common as common


class TestProjectTaskCode(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.project_task_model = self.env["project.task"]
        self.task_sequence = self.env.ref("project_task_code.sequence_task")
        self.project_task = self.env.ref("project.project_1_task_1")

    def test_old_task_code_assign(self):
        project_tasks = self.project_task_model.search([])
        for project_task in project_tasks:
            self.assertNotEqual(project_task.code, "/")

    def test_new_task_code_assign(self):
        number_next = self.task_sequence.number_next_actual
        code = self.task_sequence.get_next_char(number_next)
        project_task = self.project_task_model.create(
            {
                "name": "Testing task code",
            }
        )
        self.assertNotEqual(project_task.code, "/")
        self.assertEqual(project_task.code, code)

    def test_name_get(self):
        number_next = self.task_sequence.number_next_actual
        code = self.task_sequence.get_next_char(number_next)
        project_task = self.project_task_model.create(
            {
                "name": "Task Testing Get Name",
            }
        )
        result = project_task.name_get()
        self.assertEqual(result[0][1], "[%s] Task Testing Get Name" % code)

    def test_name_search(self):
        project_task = self.env["project.task"].create(
            {"name": "Such Much Task", "code": "TEST-123"}
        )

        result = project_task.name_search("TEST-123")
        result_ids = [item[0] for item in result]
        self.assertIn(
            project_task.id,
            result_ids,
            "Task with code %s should be in the results" % project_task.code,
        )

        result = project_task.name_search("TEST")
        result_ids = [item[0] for item in result]
        self.assertIn(
            project_task.id,
            result_ids,
            "Task with code %s should be in the results" % project_task.code,
        )

        result = project_task.name_search("much")
        result_ids = [item[0] for item in result]
        self.assertIn(
            project_task.id,
            result_ids,
            "Task with code %s should be in the results" % project_task.code,
        )

        result = project_task.name_search("20232")
        result_ids = [item[0] for item in result]
        self.assertNotIn(
            project_task.id,
            result_ids,
            "Task with code %s should not be in the results" % project_task.code,
        )

    def test_portal_self_fields_include_code(self):
        self.assertIn("code", self.project_task_model.SELF_READABLE_FIELDS)
        self.assertIn("code", self.project_task_model.SELF_WRITABLE_FIELDS)

    def test_portal_user_can_read_code_field(self):
        portal_user = common.new_test_user(
            self.env,
            login="portal_project_task_code_read",
            groups="base.group_portal",
        )
        fields = self.project_task_model.with_user(portal_user).SELF_READABLE_FIELDS
        self.assertIn("code", fields)

    def test_portal_user_can_pass_code_self_write_check(self):
        portal_user = common.new_test_user(
            self.env,
            login="portal_project_task_code_write",
            groups="base.group_portal",
        )
        self.project_task_model.with_user(portal_user)._ensure_fields_write(
            {"name": "Portal Task", "code": "TASK-001"},
            check_group_user=False,
            defaults=True,
        )
