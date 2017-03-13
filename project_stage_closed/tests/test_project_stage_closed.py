# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests import common


class TestProjectStageClosed(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestProjectStageClosed, cls).setUpClass()
        # Make sure sale_service module is installed
        module = cls.env['ir.module.module'].search(
            [('name', '=', 'sale_service')],
        )
        # Make a trick to simulate module is installed in any case
        module.state = 'installed'
        cls.task_type = cls.env['project.task.type'].create({
            'name': 'Test',
        })

    def test_closed_alias_visible(self):
        self.assertFalse(self.task_type.closed_alias_visible)
