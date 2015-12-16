# -*- coding: utf-8 -*-
from openerp.tests import common


@common.at_install(False)
@common.post_install(True)
class BusinessRequirementTestCase(common.TransactionCase):
    def setUp(self):
        super(BusinessRequirementTestCase, self).setUp()
        self.br = self.env['business.requirement']

    def test_generate_tasks_wizard(self):
        vals = {
            'name': ' test',
            'deliverable_lines': [
                (0, 0, {'description': 'task1', 'resource_time': 15.0}),
                (0, 0, {'description': 'task2', 'resource_time': 25.0}),
                (0, 0, {'description': 'task3', 'resource_time': 35.0}),
                (0, 0, {'description': 'task4', 'resource_time': 45.0}),
            ]
        }
        br = self.br.create(vals)
        action = br.generate_tasks_wizard()
        success = False
        if action:
            success = True
        self.assertTrue(success)


@common.at_install(False)
@common.post_install(True)
class BrGenerateTasksTestCase(common.TransactionCase):
    def setUp(self):
        super(BrGenerateTasksTestCase, self).setUp()
        self.br = self.env['business.requirement']
        self.wizard = self.env['br.generate.tasks']

    def test_generate_tasks(self):
        vals = {
            'name': ' test',
            'deliverable_lines': [
                (0, 0, {'description': 'task1', 'resource_time': 15.0}),
                (0, 0, {'description': 'task2', 'resource_time': 25.0}),
                (0, 0, {'description': 'task3', 'resource_time': 35.0}),
                (0, 0, {'description': 'task4', 'resource_time': 45.0}),
            ]
        }
        br = self.br.create(vals)
        action = br.generate_tasks_wizard()
        wizard_id = action.get('res_id', False)
        wizard = self.wizard.browse(wizard_id)
        tasks = wizard.generate_tasks()

        success = False
        if tasks:
            success = True
        self.assertTrue(success)
