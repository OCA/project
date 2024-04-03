from odoo import exceptions, fields
from odoo.tests.common import TransactionCase


class TestTaskDateConstraints(TransactionCase):
    def setUp(self):
        super().setUp()
        self.task = self.env["project.task"].create({"name": "test"})
        self.assertFalse(self.task.date_start)
        self.assertFalse(self.task.date_end)

    def test_valid_dates(self):
        self.task.date_start = fields.Datetime.today()
        self.task.date_end = fields.Datetime.add(self.task.date_start, days=1)
        self.assertGreater(self.task.date_end, self.task.date_start)

    def test_invalid_dates(self):
        self.task.date_start = fields.Datetime.today()
        with self.assertRaises(exceptions.ValidationError):
            self.task.date_end = fields.Datetime.subtract(self.task.date_start, days=1)
