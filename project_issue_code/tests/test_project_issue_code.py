# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestProjectIssueCode(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(TestProjectIssueCode, self).setUp(*args, **kwargs)
        # Objects
        self.obj_project_issue = self.env['project.issue']
        self.obj_ir_sequence = self.env['ir.sequence']

        # Data Sequence
        self.sequence = self.env.ref(
            'project_issue_code.project_issue_sequence')

        # Data Project Issue
        self.project_issue = self.env.ref(
            'project_issue.crm_case_buginaccountsmodule0')

    def test_assign_old_sequence(self):
        project_issue_ids = self.obj_project_issue.search([])
        for project_issue in project_issue_ids:
            self.assertNotEqual(project_issue.issue_code, '/')

    def test_assign_new_sequence(self):
        code = self.sequence.get_next_char(
            self.sequence.number_next_actual)
        project_issue = self.obj_project_issue.create({
            'name': 'Test Issue - 1',
        })
        self.assertNotEqual(project_issue.issue_code, '/')
        self.assertEqual(project_issue.issue_code, code)

    def test_copy(self):
        code = self.sequence.get_next_char(
            self.sequence.number_next_actual)
        project_issue = self.project_issue.copy()
        self.assertNotEqual(
            project_issue.issue_code, self.project_issue.issue_code)
        self.assertEqual(project_issue.issue_code, code)

    def test_custom_copy(self):
        code = 'custom'
        project_issue = self.project_issue.copy({'issue_code': code})
        self.assertNotEqual(
            project_issue.issue_code, self.project_issue.issue_code)
        self.assertEqual(project_issue.issue_code, code)
