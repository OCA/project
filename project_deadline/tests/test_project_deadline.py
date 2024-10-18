# Copyright 2019-2020 Onestein
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestProjectDeadline(TransactionCase):
    def test_fields_are_appended(self):
        view = self.env.ref("project.edit_project")
        res = self.env["project.project"].fields_view_get(view.id, "form")
        self.assertIn("date_start", res["arch"])
        self.assertIn("date", res["arch"])

    def test_other_views(self):
        view = self.env.ref("project.edit_project")
        res = self.env["project.project"].fields_view_get(view.id, "tree")
        self.assertIn("date_start", res["arch"])
        self.assertIn("date", res["arch"])
