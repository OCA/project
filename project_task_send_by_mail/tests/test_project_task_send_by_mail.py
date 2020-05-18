# Copyright 2017 Tecnativa <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestProjectTaskSendByMail(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestProjectTaskSendByMail, cls).setUpClass()
        cls.task = cls.env["project.task"].create({"name": "task test"})

    def test_send_mail(self):
        result = self.task.action_task_send()
        self.assertEqual(result["name"], "Compose Email")
