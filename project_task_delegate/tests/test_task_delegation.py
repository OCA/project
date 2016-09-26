# -*- coding: utf-8 -*-
# Copyright 2016 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.addons.mail.tests.common import TestMail
from openerp.tools import mute_logger


EMAIL_TPL = """Return-Path: <whatever-2a840@postmaster.twitter.com>
X-Original-To: {to}
Delivered-To: {to}
To: {to}
cc: {cc}
Received: by mail1.openerp.com (Postfix, from userid 10002)
    id 5DF9ABFB2A; Fri, 10 Aug 2012 16:16:39 +0200 (CEST)
Message-ID: {msg_id}
Date: Tue, 29 Nov 2011 12:43:21 +0530
From: {email_from}
MIME-Version: 1.0
Subject: {subject}
Content-Type: text/plain; charset=ISO-8859-1; format=flowed

Hello,

This email should create a new entry in your module. Please check that it
effectively works.

Thanks,

--
Raoul Boitempoils
Integrator at Agrolait"""


class TestTaskDelegation(TestMail):

    @classmethod
    def setUpClass(cls):
        super(TestTaskDelegation, cls).setUpClass()
        cls.project_task_delegate = cls.env['project.task.delegate']
        user_group_employee = cls.env.ref('base.group_user')
        user_group_project_user = cls.env.ref('project.group_project_user')

        Users = cls.env['res.users'].with_context({'no_reset_password': True})
        cls.user_projectuser = Users.create({
            'name': 'Dhinesh ProjectUser',
            'login': 'Dhinesh',
            'alias_name': 'dhinesh',
            'email': 'dhinesh.projectuser@example.com',
            'groups_id': [(6, 0, [user_group_employee.id,
                                  user_group_project_user.id])]
        })
        cls.project_goats = cls.env['project.project'].with_context(
            {'mail_create_nolog': True}).create({
                'name': 'Goats',
                'privacy_visibility': 'portal',
                'alias_name': 'project+goats',
                'partner_id': cls.partner_1.id,
                'type_ids': [
                    (0, 0, {
                        'name': 'New',
                        'sequence': 1,
                    }),
                    (0, 0, {
                        'name': 'Won',
                        'sequence': 10,
                    })]
            })

    @mute_logger('openerp.addons.mail.mail_thread')
    def test_task_delegation(self):
        task = self.format_and_process(
            EMAIL_TPL,
            to='project+goats@mydomain.com, valid.lelitre@agrolait.com',
            cc='valid.other@gmail.com',
            email_from='%s' % self.user_projectuser.email,
            subject='Cats',
            msg_id='<1198923581.41972151344608186760.JavaMail@agrolait.com>',
            target_model='project.task')
        self.assertEqual(len(task), 1, 'project_task_delegate: '
                         'test_task_delegation: a new project.task '
                         'should have been created')
        # Open the delegation wizard
        delegate_id = self.project_task_delegate.with_context(
            {'active_id': task.id}).create({
                'user_id': self.user_projectuser.id,
                'planned_hours': 12.0,
                'planned_hours_me': 2.0,
            })
        self.assertEqual(len(delegate_id), 1, 'project_task_delegate: '
                         'test_task_delegation: a new project.task.delegate '
                         'should have been created')
        delegate_id.with_context({'active_id': task.id}).delegate()
        # Check delegation details
        task.invalidate_cache()
        self.assertEqual(task.planned_hours, 2, 'project_task_delegate: '
                         'test_task_delegation: planned hours is not correct')
