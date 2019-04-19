# Copyright 2016 - Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestProjectTaskDigitizedSignature(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestProjectTaskDigitizedSignature, cls).setUpClass()
        cls.task = cls.env['project.task'].create({
            'name': 'Task test #1',
        })

    def test_task_digitized_signature(self):
        search_domain = [
            ('model', '=', 'project.task'),
            ('res_id', '=', self.task.id),
            ('body', 'like', 'Signature has been created%'),
        ]
        # There is not messages created
        messages = self.env['mail.message'].search(search_domain)
        self.assertEqual(len(messages.ids), 0)
        # We add signature and write. Message must be created.
        self.task.customer_signature = \
            'R0lGODlhAQABAIAAAMLCwgAAACH5BAAAAAAALAAAAAABAAEAAAICRAEAOw =='
        messages = self.env['mail.message'].search(search_domain)
        self.assertEqual(len(messages.ids), 1)
        # We create a new one. Message must be created.
        self.task = self.env['project.task'].create({
            'name': 'Task test #2',
            'customer_signature':
                'R0lGODlhAQABAIAAAMLCwgAAACH5BAAAAAAALAAAAAABAAEAAAICRAEAOw =='
        })
        messages = self.env['mail.message'].search(search_domain)
        self.assertEqual(len(messages.ids), 1)
