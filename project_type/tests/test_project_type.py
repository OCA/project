# Copyright 2019 Onestein
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestProjectType(TransactionCase):
    def setUp(self):
        super(TestProjectType, self).setUp()
        self.cat = self.env["project.type"].create({"name": "General"})
        self.cat2 = self.env["project.type"].create({"name": "Discussion"})

    def test_complete_name(self):
        self.cat2.parent_id = self.cat.id
        self.assertEqual(self.cat.complete_name, "General")
        self.assertEqual(self.cat2.complete_name, "General / Discussion")

    def test_no_recursion(self):
        self.cat2.parent_id = self.cat.id
        with self.assertRaises(ValidationError):
            self.cat.parent_id = self.cat2.parent_id.id
