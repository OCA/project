# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import TransactionCase


class TestProjectTask(TransactionCase):
    def setUp(self):
        super(TestProjectTask, self).setUp()

        self.task_3 = self.env['project.task'].browse(
            self.ref("project_task_employee.restricted_task_3"))
        self.task_2 = self.env['project.task'].browse(
            self.ref("project_task_employee.restricted_task_2"))
        self.task_7 = self.env['project.task'].browse(
            self.ref("project_task_employee.restricted_task_7"))
        self.task_1 = self.env['project.task'].browse(
            self.ref("project_task_employee.restricted_task_1"))

    def test_employee_domain_ids(self):
        jth = self.env['hr.employee'].browse(self.ref("hr.employee_jth"))
        root = self.env['hr.employee'].browse(self.ref("hr.employee_root"))

        self.assertEqual(self.task_3.employee_domain_ids, jth + root)
        self.assertEqual(self.task_2.employee_domain_ids, jth + root)
        self.assertEqual(self.task_7.employee_domain_ids, root)
        self.assertEqual(self.task_1.employee_domain_ids, jth)
