# Copyright 2016 Tecnativa <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.base.tests.common import BaseCommon


class TestProjectTaskCode(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.project_task_model = cls.env["project.task"]
        cls.ir_sequence_model = cls.env["ir.sequence"]
        cls.task_sequence = cls.env.ref("project_task_code.sequence_task")

    def test_old_task_code_assign(self):
        project_tasks = self.project_task_model.search([])
        for project_task in project_tasks:
            self.assertNotEqual(project_task.code, "/")

    def test_new_task_code_assign(self):
        number_next = self.task_sequence.number_next_actual
        code = self.task_sequence.get_next_char(number_next)
        project_task = self.project_task_model.create({"name": "Testing task code"})
        self.assertNotEqual(project_task.code, "/")
        self.assertEqual(project_task.code, code)

    def test_name_get(self):
        number_next = self.task_sequence.number_next_actual
        code = self.task_sequence.get_next_char(number_next)
        project_task = self.project_task_model.create({"name": "Task Testing Get Name"})
        result = project_task.display_name
        # Check by regex, as the display name can be modified in other modules
        self.assertRegex(result, f"\\[{code}\\]")

    def test_name_search(self):
        project_task = self.env["project.task"].create(
            {"name": "Such Much Task", "code": "TEST-123"}
        )

        result = project_task.name_search("TEST-123")
        self.assertIn(
            project_task.id,
            map(lambda x: x[0], result),
            f"Task with code {project_task.code} should be in the results",
        )

        result = project_task.name_search("TEST")
        self.assertIn(
            project_task.id,
            map(lambda x: x[0], result),
            f"Task with code {project_task.code} should be in the results",
        )

        result = project_task.name_search("much")
        self.assertIn(
            project_task.id,
            map(lambda x: x[0], result),
            f"Task with code {project_task.code} should be in the results",
        )

        result = project_task.name_search("20232")
        self.assertNotIn(
            project_task.id,
            map(lambda x: x[0], result),
            f"Task with code {project_task.code} should not be in the results",
        )
