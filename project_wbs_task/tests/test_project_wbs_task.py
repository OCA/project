# Copyright 2017 ForgeFlow S.L.
# Copyright 2017 Matmoz d.o.o.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.addons.project_wbs.tests import test_project_wbs


class TestProjectWbsTask(test_project_wbs.TestProjectWbs):
    def setUp(self):
        super(TestProjectWbsTask, self).setUp()
        self.task = self.env['project.task'].create({
            'name': 'Test Task',
            'project_id': self.project_grand_son.id})

    def test_search_task(self):
        task = self.env['project.task'].search(
            [('project_complete_wbs_code', '=', '[0001 / 01 / 02]')])
        self.assertEqual(len(task), 1, 'should find task with wbs code')
        task = self.env['project.task'].search(
            [('project_complete_wbs_name', '=',
              'Test project / Test project son / Test project grand son')])
        self.assertEqual(len(task), 1, 'should find task with wbs name')

    def test_check_analytic(self):
        self.assertEqual(self.task.analytic_account_id, self.grand_son_account)
