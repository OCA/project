# -*- coding: utf-8 -*-
# Copyright 2016-2017 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.html).

from odoo.tests import common
from odoo import exceptions
from ..hooks import post_init_hook, uninstall_hook


class TestProjectDoubleAlias(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestProjectDoubleAlias, cls).setUpClass()
        cls.project = cls.env['project.project'].create({
            'name': 'Test project',
            'use_tasks': True,
            'use_issues': True,
            'second_alias_name': 'test_second',
        })
        cls.issue_model = cls.env['ir.model'].search(
            [('model', '=', 'project.issue')])
        cls.env['ir.config_parameter'].set_param(
            "mail.catchall.domain", "test.com",
        )

    def test_second_alias(self):
        self.assertTrue(self.project.second_alias_id)
        self.assertEqual(self.project.second_alias_id.alias_name,
                         self.project.second_alias_name)
        self.assertEqual(
            self.project.second_alias_id.alias_model_id, self.issue_model)
        self.assertEqual(self.project.second_alias_id.alias_parent_thread_id,
                         self.project.id)
        self.project.alias_contact = 'followers'
        second_alias = self.project.second_alias_id
        self.assertEqual(second_alias.alias_contact, 'followers')
        self.project.unlink()
        self.assertFalse(second_alias.exists())

    def test_change_second_alias(self):
        self.project.second_alias_name = 'Test 2'
        self.assertEqual(self.project.second_alias_id.alias_name,
                         self.project.second_alias_name)

    def test_change_second_alias_from_empty(self):
        project2 = self.env['project.project'].create(
            {'name': 'Test project 2'})
        project2.second_alias_name = 'test-2'
        self.assertTrue(project2.second_alias_id)
        self.assertEqual(
            project2.second_alias_id.alias_name, project2.second_alias_name)
        self.assertEqual(
            project2.second_alias_id.alias_model_id, self.issue_model)
        self.assertEqual(
            project2.second_alias_id.alias_parent_thread_id, project2.id)

    def test_change_second_alias_to_empty(self):
        self.project.second_alias_name = ''
        self.assertFalse(self.project.second_alias_id)
        alias = self.env['mail.alias'].search(
            [('alias_parent_thread_id', '=', self.project.id),
             ('alias_model_id', '=', self.issue_model.id)])
        self.assertFalse(alias)

    def test_existing_alias(self):
        with self.assertRaises(exceptions.ValidationError):
            self.env['project.project'].create({
                'name': 'Test project 2',
                'second_alias_name': 'test_second',
            })

    def test_hooks(self):
        project2 = self.env['project.project'].create(
            {'name': 'Test project 2',
             'second_alias_name': 'test-2'})
        project2.alias_id.alias_name = False
        # Project for trying the alias search in the hook
        project3 = self.env['project.project'].create(
            {'name': 'Test project 3',
             'second_alias_name': 'test-3'})
        project3.second_alias_id = False
        uninstall_hook(self.env.cr, self.registry)
        self.assertEqual(project2.alias_id.alias_name, 'test-2')
        post_init_hook(self.env.cr, self.registry)
        self.assertFalse(project2.alias_id.alias_name)
        self.assertEqual(project2.second_alias_id.alias_name, 'test-2')
        self.assertTrue(project3.second_alias_id)

    def test_reply_to(self):
        issue = self.env['project.issue'].create({
            'project_id': self.project.id,
            'name': 'Test issue',
        })
        reply = issue.message_get_reply_to(issue.ids)
        self.assertIn(self.project.second_alias_name, reply[issue.id])
        task = self.env['project.task'].create({
            'project_id': self.project.id,
            'name': 'Test task',
        })
        reply = task.message_get_reply_to(task.ids)
        self.assertIn(self.project.alias_name, reply[task.id])
