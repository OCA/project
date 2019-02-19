# Copyright 2018 Onestein
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestCriticalPath(TransactionCase):
    def test_diff_project_critical_path(self):
        project_obj = self.env['project.project']
        project1 = project_obj.create({
            'name': 'Project Critical Path Test Uno'
        })
        project2 = project_obj.create({
            'name': 'Project Critical Path Test Dos'
        })

        task_obj = self.env['project.task']
        task1 = task_obj.create({
            'name': 'Task Critical Path Test Uno',
            'project_id': project1.id
        })
        task2 = task_obj.create({
            'name': 'Task Critical Path Test Dos',
            'project_id': project2.id,
            'dependency_task_ids': [(4, task1.id)]
        })
        critical_path = project_obj.calc_critical_paths([project2.id])
        self.assertEqual(critical_path, {
            project2.id: [task1.id, task2.id]
        })

    def test_critical_path_duration(self):
        task_obj = self.env['project.task']
        task1 = task_obj.create({
            'name': 'Task Critical Path Test Tres',
            'date_start': '2018-01-20 00:00:00',
            'date_end': '2018-01-25 00:00:00',
            'planned_hours': 4
        })

        task1.company_id.critical_path_duration_base = 'date'
        self.assertEqual(task1.critical_path_duration, 5 * 3600 * 24)
        task1.company_id.critical_path_duration_base = 'planned_hours'
        self.assertEqual(task1.critical_path_duration, 4)
