# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestTask(TransactionCase):
    def setUp(self, *args, **kwargs):
        result = super(TestTask, self).setUp(*args, **kwargs)
        # Setup Stage States
        self.env.ref('project.project_tt_analysis').state = 'draft'
        self.env.ref('project.project_tt_development').state = 'open'
        self.env.ref('project.project_tt_deployment').state = 'done'
        # Set self.env to use Demo user
        self.root = self.env
        demo_user = self.root.env.ref('base.demo_user')
        self.env = self.root(user=demo_user)
        # Create test Task
        self.task1 = self.env['project.task'].create({
            'name': 'Test Task 1',
            'project_id': self.ref('project.project_project_1'),
            })
        return result

    def test_task_statistics(self):
        """Test Date Opened and Date Closed calculation"""
        # Setup shortcuts
        t1 = self.task1
        stage_new = self.env.ref('project.project_tt_analysis')
        stage_open = self.env.ref('project.project_tt_development')
        stage_done = self.env.ref('project.project_tt_deployment')
        self.assertEqual(
            t1.stage_id, stage_new,
            'Task created in Analysis stage')
        self.assertIsNone(t1.date_opened, 'New task cannot have open date')
        self.assertIsNone(t1.date_closed, 'New task cannot have close date')
        # Done task
        t1.stage_id = stage_done
        self.assertIsNotNone(t1.date_opened, 'Done task must have open date')
        self.assertIsNotNone(t1.date_closed, 'Done task must have close date')
        # (Re)Open task
        t1.stage_id = stage_open
        self.assertIsNotNone(t1.date_opened, 'Open task must have open date')
        self.assertIsNone(t1.date_closed, 'Open task cannot have close date')
