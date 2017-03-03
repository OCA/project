# -*- coding: utf-8 -*-
# Copyright 2017 Specialty Medical Drugstore
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestProjectTaskPullRequest(TransactionCase):

    def setUp(self):
        super(TestProjectTaskPullRequest, self).setUp()
        self.project_1 = self.env['project.project'].create({
            'name': 'Test Project',
            'pr_required_states': [(4, 6, 0)],
        })
        self.project_2 = self.env['project.project'].create({
            'name': 'Test Project',
            'pr_required_states': [(4, 6, 0), (4, 5, 0)],
        })
        self.task_1 = self.env['project.task'].create({
            'name': 'Test Task',
            'project_id': self.project_1.id,
            'pr_uri': False,
            'stage_id': 1,
        })
        self.task_2 = self.env['project.task'].create({
            'name': 'Test Task',
            'project_id': self.project_2.id,
            'pr_uri': False,
            'stage_id': 1,
        })
        self.task_3 = self.env['project.task'].create({
            'name': 'Test Task',
            'project_id': self.project_2.id,
            'pr_uri': 'github.com',
            'stage_id': 1,
        })

    def test_write_allowed_when_allowed(self):
        self.task_1.write({'stage_id': 3, })
        self.task_1.refresh()
        self.assertEquals(3, self.task_1.stage_id.id)

    def test_write_not_allowed_without_pr(self):
        with self.assertRaises(ValidationError):
            self.task_1.write({'stage_id': 6, })

    def test_write_not_allowed_without_pr_multiple_stages(self):
        with self.assertRaises(ValidationError):
            self.task_2.write({'stage_id': 6, })

    def test_write_allowed_with_pr(self):
        self.task_3.write({'stage_id': 6, })
        self.task_3.refresh()
        self.assertEquals(6, self.task_3.stage_id.id)
