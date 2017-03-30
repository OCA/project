# coding: utf-8
# © 2017 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase
from odoo import SUPERUSER_ID
from ..models.action import UNIQUE_ACTION_ID


class TestProjectRelatedTask(TransactionCase):

    def test_goto_document(self):
        task = self.env.ref('project_model_to_task.relative_task')
        res = task.goto_document()
        self.assertEqual(res.get('res_id'), self.env.ref(
            'project.project_task_6').id)

    def test_check_ir_values(self):
        values = self.env['ir.values'].get_actions(
            'client_action_multi', 'res.partner')
        my_val = False
        for value in values:
            if value[0] == UNIQUE_ACTION_ID:
                my_val = UNIQUE_ACTION_ID
                # prevent to add multiple times the same action
                break
        self.assertEqual(my_val, UNIQUE_ACTION_ID)

    def test_create_related_task(self):
        user = self.env['res.users'].browse(SUPERUSER_ID)
        ctx = {
            'active_id': user.id,
            'active_ids': user.ids,
            'active_model': 'res.users',
        }
        action = self.env.ref(
            'project_model_to_task.task_from_elsewhere')
        res = action.with_context(ctx).read()
        self.assertEqual(res[0]['context'].get('from_model'), 'res.users')
        self.assertEqual(res[0]['context'].get('from_id'), user.id)
