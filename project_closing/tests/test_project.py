# -*- coding: utf-8 -*-
from odoo import tests


class TestProject(tests.TransactionCase):
    def setUp(self):
        super(TestProject, self).setUp()
        self._project = self.env['project.project'].create({
            'name': "Some test project"
        })

    def test_toggle_active(self):
        self.assertTrue(self._project.active)
        self.assertTrue(self._project.analytic_account_id.active)
        self._project.toggle_active()
        self.assertFalse(self._project.active)
        self.assertFalse(self._project.analytic_account_id.active)
        self._project.toggle_active()
        self.assertTrue(self._project.active)
        self.assertTrue(self._project.analytic_account_id.active)
