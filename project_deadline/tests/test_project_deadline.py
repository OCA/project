# Copyright 2019 Onestein
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestProjectDeadline(SavepointCase):
    def test_fields_are_appended(self):
        view = self.env.ref('project.edit_project')
        res = self.env['project.project'].fields_view_get(view.id, 'form')
        self.assertIn('date_start', res['arch'])
        self.assertIn('date', res['arch'])

    def test_other_views(self):
        view = self.env.ref('project.edit_project')
        res = self.env['project.project'].fields_view_get(view.id, 'tree')

        # It should not affect other view types
        self.assertNotIn('date_start', res['arch'])
        self.assertNotIn('date', res['arch'])
