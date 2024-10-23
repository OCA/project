# Copyright 2016 - Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestProjectTaskDigitizedSignature(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestProjectTaskDigitizedSignature, cls).setUpClass()
        cls.task = cls.env["project.task"].create({"name": "Task test #1"})

    def test_task_digitized_signature(self):
        # We add signature and write.
        self.task.customer_signature = (
            "R0lGODlhAQABAIAAAMLCwgAAACH5BAAAAAAALAAAAAABAAEAAAICRAEAOw =="
        )
        # We create a new one.
        sign = "R0lGODlhAQABAIAAAMLCwgAAACH5BAAAAAAALAAAAAABAAEAAAICRAEAOw =="
        self.task = self.env["project.task"].create(
            {"name": "Task test #2", "customer_signature": sign}
        )
