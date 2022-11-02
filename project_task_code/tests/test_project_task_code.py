# Copyright 2016 Tecnativa <vicent.cubells@tecnativa.com>
# Copyright 2023 Abraham Anes <abrahamanes@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import odoo.tests.common as common
from odoo.exceptions import ValidationError


class TestProjectTaskCode(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.project_task_model = cls.env["project.task"]
        cls.task_sequence = cls.env["ir.sequence"].create(
            {"name": "Test sequence", "padding": 5, "prefix": "TESTASK"}
        )
        cls.project_task = cls.env.ref("project.project_1_task_1")
        cls.company_1 = cls.env.ref("base.main_company")

    def test_old_task_code_assign(self):
        project_tasks = self.project_task_model.search([])
        for project_task in project_tasks:
            self.assertEqual(project_task.code, "/")

    def test_new_task_code_assign(self):
        self.company_1.project_task_seq_id = self.task_sequence.id
        number_next = self.company_1.project_task_seq_id.number_next_actual
        code = self.company_1.project_task_seq_id.get_next_char(number_next)
        project_task = self.project_task_model.create(
            {"name": "Testing task code", "company_id": self.company_1.id}
        )
        self.assertNotEqual(project_task.code, "/")
        self.assertEqual(project_task.code, code)

    def test_name_get(self):
        number_next = self.task_sequence.number_next_actual
        code = self.task_sequence.get_next_char(number_next)
        self.company_1.project_task_seq_id = self.task_sequence.id
        project_task = self.project_task_model.create(
            {
                "name": "Task Testing Get Name",
            }
        )
        result = project_task.name_get()
        self.assertEqual(result[0][1], "[%s] Task Testing Get Name" % code)

    def test_unique_task_code(self):
        # Enable unique task code constraint
        self.company_1.project_task_seq_id = self.task_sequence.id

        project_task = self.project_task_model.create({"name": "Testing task code"})
        with self.assertRaises(ValidationError):
            self.project_task_model.create(
                {"name": "Testing task code", "code": project_task.code}
            )
