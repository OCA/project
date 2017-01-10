# -*- coding: utf-8 -*-
# Copyright 2016 - Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests import common
from openerp import exceptions


class TestProjectIssueTask(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestProjectIssueTask, cls).setUpClass()
        cls.issue = cls.env['project.issue'].create({
            'name': 'issue for test',
        })
        cls.stage_fold = cls.env['project.task.type'].create({
            'name': 'task to fold',
            'fold': True,
        })
        cls.stage_no_fold = cls.env['project.task.type'].create({
            'name': 'task not to fold',
            'fold': False,
        })

    def test_task_from_issue(self):
        res = self.issue.action_create_task()
        self.assertEqual(res.get('res_id'), self.issue.task_id.id)
        self.assertTrue(self.issue.task_id)
        with self.assertRaises(exceptions.UserError):
            self.issue.action_create_task()
        task = self.issue.task_id
        task.stage_id = self.stage_no_fold.id
        self.assertFalse(self.issue.stage_id.fold)
        task.stage_id = self.stage_fold.id
        self.assertTrue(self.issue.stage_id.fold)
        self.assertEqual(task.issue_id, self.issue)
