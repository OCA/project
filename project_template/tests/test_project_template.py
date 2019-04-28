# -*- coding: utf-8 -*-
# Copyright 2019 Thore Baden
# Copyright 2019 Benjamin Brich
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestProjectTemplate(TransactionCase):
    def setUp(self):
        super(TestProjectTemplate, self).setUp()
        self.user_noone = self.env['res.users'].with_context(
            {
                'no_reset_password': True,
                'mail_create_nosubscribe': True
            }).create({
                'name': 'Noemie NoOne',
                'login': 'noemie',
                'email': 'n.n@example.com',
                'signature': '--\nNoemie',
                'groups_id': [(6, 0, [])]
            })
        self.project_pig = self.env['project.project'].with_context(
            {'mail_create_nolog': True}).create({
                'name': 'Pigs',
                'privacy_visibility': 'employees',
                'is_template': True
            })
        self.task_1 = self.env['project.task'].with_context(
            {'mail_create_nolog': True}).create({
                'name': 'Test1', 'user_id': self.user_noone.id,
                'project_id': self.project_pig.id
            })
        self.task_2 = self.env['project.task'].with_context(
            {'mail_create_nolog': True}).create({
                'name': 'Test2', 'user_id': self.user_noone.id,
                'project_id': self.project_pig.id
            })

    def test_template_create_with_template_id(self):
        project_pig = self.project_pig
        project_pig_with_template = self.env['project.project'].with_context(
            {'mail_create_nolog': True}).create({
                'name': 'New Pigs',
                'privacy_visibility': 'followers',
                'template_id': project_pig.id
            })
        self.assertEqual(
            project_pig.privacy_visibility,
            project_pig_with_template.privacy_visibility
        )
        self.assertEqual(
            project_pig.task_count,
            project_pig_with_template.task_count
        )

    def test_template_create_without_template_id(self):
        project_pig = self.project_pig
        project_pig_with_template = self.env['project.project'].with_context(
            {'mail_create_nolog': True}).create({
                'name': 'New Pigs',
                'privacy_visibility': 'followers',
                'template_id': False
            })
        self.assertNotEqual(
            project_pig.privacy_visibility,
            project_pig_with_template.privacy_visibility
        )
        self.assertNotEqual(
            project_pig.task_count,
            project_pig_with_template.task_count
        )

    def test_template_flag_copy(self):
        project = self.env['project.project'].create({
            'name': '1',
            'is_template': True,
        })
        new_project = project.copy()
        self.assertNotEqual(project.is_template, new_project.is_template)

    def test_toggle_template(self):
        project_pig = self.project_pig
        self.assertEqual(project_pig.is_template, True)
        project_pig.toggle_template()
        self.assertEqual(project_pig.is_template, False)
