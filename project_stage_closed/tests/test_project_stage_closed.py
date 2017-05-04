# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


class TestProjectStageClosed(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestProjectStageClosed, cls).setUpClass()
        cls.stage = cls.env['project.stage.type'].create({
            'name': 'Test stage',
            'closed': True,
        })
