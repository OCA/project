# Copyright 2018 PESOL (http://pesol.es)
#                Angel Moya (angel.moya@pesol.es)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo.tests.common import TransactionCase


class TestProjectTaskDefaultTags(TransactionCase):

    def setUp(self):
        super(TestProjectTaskDefaultTags, self).setUp()
        self.tag_A = self.env['project.tags'].create({
            'name': 'Tag Test A'})
        self.tag_B = self.env['project.tags'].create({
            'name': 'Tag Test B'})
        self.project_A = self.env['project.project'].create({
            'name': 'Project Test A',
            'tag_ids': [(6, 0, self.tag_A.ids)]
        })
        self.project_B = self.env['project.project'].create({
            'name': 'Project Test B',
            'tag_ids': [(6, 0, self.tag_B.ids)]
        })
        self.task = self.env['project.task'].with_context({
            'default_project_id': self.project_A.id
        }).create({
            'name': 'Task Test',
        })

    def test_new_task(self):
        self.assertEqual(self.task.tag_ids, self.project_A.tag_ids)

    def test_onchange_project_task(self):
        self.task.project_id = self.project_B
        self.task._onchange_project_id()
        self.assertEqual(self.task.tag_ids, self.project_B.tag_ids)
