# -*- coding: utf-8 -*-
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.html).

from openerp.tests import common
from openerp import exceptions
from ..hooks import post_init_hook, uninstall_hook


class TestProjectDoubleAlias(common.TransactionCase):
    def setUp(self):
        super(TestProjectDoubleAlias, self).setUp()
        self.project = self.env['project.project'].create({
            'name': 'Test project',
            'second_alias_name': 'test',
        })
        self.issue_model = self.env['ir.model'].search(
            [('model', '=', 'project.issue')])

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
                'second_alias_name': 'test',
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
