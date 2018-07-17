# Copyright 2016-2018 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestProjectTaskDependency(TransactionCase):

    def setUp(self):
        super(TestProjectTaskDependency, self).setUp()
        self.task1 = self.env['project.task'].create({
            'name': '1',
            'date_start': '2018-01-01 00:00:00'
        })
        self.task2 = self.env['project.task'].create({
            'name': '2',
            'dependency_task_ids': [(6, 0, [self.task1.id])],
            'date_start': '2018-01-01 00:00:00',
            'date_end': '2018-01-08 00:00:00'
        })
        self.task3 = self.env['project.task'].create({
            'name': '3',
            'dependency_task_ids': [(6, 0, [self.task2.id])],
            'date_start': '2018-01-08 00:00:00',
            'date_end': '2018-01-15 00:00:00'
        })

    def test_01_dependency_path(self):
        self.assertEqual(len(self.task3.dependency_task_ids), 1)

        self.assertEqual(len(self.task1.recursive_dependency_task_ids), 0)
        self.assertEqual(len(self.task3.recursive_dependency_task_ids), 2)

        self.assertEqual(len(self.task3.depending_task_ids), 0)
        self.assertEqual(len(self.task1.depending_task_ids), 1)

        self.assertEqual(len(self.task3.recursive_depending_task_ids), 0)
        self.assertEqual(len(self.task1.recursive_depending_task_ids), 2)

    def test_02_avoid_recursion(self):
        with self.assertRaises(ValidationError):
            self.task1.write({
                'dependency_task_ids': [(6, 0, [self.task3.id])]
            })

    def test_arrange(self):
        self.env['ir.config_parameter'].set_param(
            'project_task_dependency.task_dependency_arrange',
            True
        )

        self.task1.write({
            'date_start': '2017-01-01 00:00:00'
        })

        self.assertEqual(self.task2.date_start, '2018-01-01 00:00:00')
        self.assertEqual(self.task2.date_end, '2018-01-08 00:00:00')
        self.assertEqual(self.task3.date_start, '2018-01-08 00:00:00')
        self.assertEqual(self.task3.date_end, '2018-01-15 00:00:00')

        self.task1.write({
            'date_start': '2018-01-08 00:00:00'
        })

        self.assertEqual(self.task2.date_start, '2018-01-08 00:00:00')
        self.assertEqual(self.task2.date_end, '2018-01-15 00:00:00')
        self.assertEqual(self.task3.date_start, '2018-01-15 00:00:00')
        self.assertEqual(self.task3.date_end, '2018-01-22 00:00:00')

        self.task2.write({
            'date_start': '2017-12-01 00:00:00',
            'date_end': '2018-01-22 00:00:00'
        })

        self.assertEqual(self.task1.date_start, '2017-12-01 00:00:00')
        self.assertEqual(self.task3.date_start, '2018-01-22 00:00:00')
        self.assertEqual(self.task3.date_end, '2018-01-29 00:00:00')

        self.task3.write({
            'date_start': '2018-01-21 00:00:00',
            'date_end': '2018-01-28 00:00:00'
        })

        self.assertEqual(self.task1.date_start, '2017-11-30 00:00:00')
        self.assertEqual(self.task2.date_start, '2017-11-30 00:00:00')
        self.assertEqual(self.task2.date_end, '2018-01-21 00:00:00')
        self.assertEqual(self.task3.date_start, '2018-01-21 00:00:00')
        self.assertEqual(self.task3.date_end, '2018-01-28 00:00:00')
