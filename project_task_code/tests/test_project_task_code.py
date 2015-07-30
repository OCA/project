# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

import openerp.tests.common as common


class TestProjectTaskCode(common.TransactionCase):

    def setUp(self):
        super(TestProjectTaskCode, self).setUp()
        self.project_task_model = self.env['project.task']
        self.ir_sequence_model = self.env['ir.sequence']
        self.task_sequence = self.env.ref('project_task_code.sequence_task')
        self.project_task = self.env.ref('project.project_task_1')

    def test_old_task_code_assign(self):
        project_tasks = self.project_task_model.search([])
        for project_task in project_tasks:
            self.assertNotEqual(project_task.code, '/')

    def test_new_task_code_assign(self):
        code = self._get_next_code()
        project_task = self.project_task_model.create({
            'name': 'Testing task code',
        })
        self.assertNotEqual(project_task.code, '/')
        self.assertEqual(project_task.code, code)

    def test_copy_task_code_assign(self):
        code = self._get_next_code()
        project_task_copy = self.project_task.copy()
        self.assertNotEqual(project_task_copy.code, self.project_task.code)
        self.assertEqual(project_task_copy.code, code)

    def _get_next_code(self):
        d = self.ir_sequence_model._interpolation_dict()
        prefix = self.ir_sequence_model._interpolate(
            self.task_sequence.prefix, d)
        suffix = self.ir_sequence_model._interpolate(
            self.task_sequence.suffix, d)
        code = (prefix + ('%%0%sd' % self.task_sequence.padding %
                          self.task_sequence.number_next_actual) + suffix)
        return code
