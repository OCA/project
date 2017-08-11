# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests import common


class TestProjectChangeState(common.TransactionCase):
    def setUp(self):
        super(TestProjectChangeState, self).setUp()
        self.project_model = self.env['project.project']
        self.project1 = self.create_project('test1')
        self.project2 = self.create_project('test2')
        self.wizard_model = self.env['project.change.state'].with_context(
            active_ids=[self.project1.id, self.project2.id])

    def create_project(self, name):
        return self.project_model.create({'name': name})

    def test_set_pending(self):
        self.wizard_model.set_pending()
        self.assertEqual(
            self.project1.state, 'pending', 'Project 1 not pending')
        self.assertEqual(
            self.project2.state, 'pending', 'Project 2 not pending')

    def test_set_open(self):
        self.wizard_model.set_open()
        self.assertEqual(
            self.project1.state, 'open', 'Project 1 not open')
        self.assertEqual(
            self.project2.state, 'open', 'Project 2 not open')

    def test_set_done(self):
        self.wizard_model.set_done()
        self.assertEqual(
            self.project1.state, 'close', 'Project 1 not close')
        self.assertEqual(
            self.project2.state, 'close', 'Project 2 not close')

    def test_set_cancel(self):
        self.wizard_model.set_cancel()
        self.assertEqual(
            self.project1.state, 'cancelled', 'Project 1 not cancelled')
        self.assertEqual(
            self.project2.state, 'cancelled', 'Project 2 not cancelled')
