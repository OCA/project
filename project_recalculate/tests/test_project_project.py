# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp.exceptions import Warning
from openerp.fields import DATE_LENGTH
from . import base

project_final_dates_one_task = {
    'date_begin': (
        # name, start_date, end date
        ('pj_0', '2015-08-01', '2015-08-05'),
        ('pj_1', '2015-08-02', '2015-08-05'),
        ('pj_2', '2015-08-03', '2015-08-05'),
    ),
    'date_end': (
        ('pj_0', '2015-08-10', '2015-10-03'),
        ('pj_1', '2015-08-17', '2015-10-10'),
        ('pj_2', '2015-08-21', '2015-10-17'),
    ),
}

n_projects = base.n_projects
project_date_cases = base.project_init_dates
total_tasks = base.n_tasks
task_days_cases = base.task_days
project_dates_res = {
    'no_tasks': {
        'date_begin': base.project_init_dates,
        'date_end': base.project_init_dates,
    },
    'one_task': project_final_dates_one_task,
    'tasks': base.project_final_dates,
}
task_dates_res = base.task_dates


# One test case per method
class TestProjectProjectBegin(base.BaseCase):
    calculation_type = 'date_begin'

    #####################################################################
    # Check _start_end_dates_prepare
    #   * With no tasks: date is the same
    #   * With one task: date is task end date
    #   * With several tasks: date is latest task end date
    def _start_end_dates_prepare(self, n_tasks, res=False):
        counter = 0
        for n, sd, ed in project_date_cases:
            project = self.project_create(n, n_tasks, {
                'calculation_type': self.calculation_type,
                'date_start': sd,
                'date': ed,
            })
            if n_tasks > 0:
                self.project_task_dates_set(
                    project, task_dates_res[self.calculation_type][n])
            vals = project._start_end_dates_prepare()
            if res:
                dates = res[self.calculation_type][counter]
                if self.calculation_type == 'date_begin':
                    self.assertEqual(
                        vals.get('date', False), dates[2],
                        "[%d] FAIL: date" % counter)
                else:
                    self.assertEqual(
                        vals.get('date_start', False), dates[1],
                        "[%d] FAIL: date_start" % counter)
            else:
                self.assertEqual(vals, {})
            counter += 1

    def test_start_end_dates_prepare_no_task(self):
        self._start_end_dates_prepare(0)

    def test_start_end_dates_prepare_one_task(self):
        self._start_end_dates_prepare(1, res=project_dates_res['one_task'])

    def test_start_end_dates_prepare_tasks(self):
        self._start_end_dates_prepare(total_tasks,
                                      res=project_dates_res['tasks'])

    #####################################################################
    # Check project_recalculate
    #   * With no tasks
    #   * With one task
    #   * With several tasks
    def _project_recalculate(self, n_tasks, res_p, res_t=False):
        counter = 0
        for n, sd, ed in project_date_cases:
            project = self.project_create(n, n_tasks, {
                'calculation_type': self.calculation_type,
                'date_start': sd,
                'date': ed,
            })
            if n_tasks > 0:
                self.project_task_days_set(
                    project, task_days_cases[self.calculation_type])
            project.project_recalculate()
            # Check project dates
            dates = res_p[self.calculation_type][counter]
            self.assertEqual(
                project.date_start, dates[1],
                "[%d] FAIL: project date_start" % counter)
            self.assertEqual(
                project.date, dates[2],
                "[%d] FAIL: project date" % counter)
            # Check task dates
            for i in range(0, n_tasks):
                dates = res_t[self.calculation_type][n][i]
                task = project.tasks.filtered(
                    lambda r: r.name == dates[0])
                self.assertEqual(
                    task.date_start[:DATE_LENGTH], dates[1],
                    "[%d, %d] FAIL: task date_start" % (counter, i))
                self.assertEqual(
                    task.date_end[:DATE_LENGTH], dates[2],
                    "[%d, %d] FAIL: task date_end" % (counter, i))
            counter += 1

    def test_project_recalculate_no_task(self):
        self._project_recalculate(0, project_dates_res['no_tasks'])

    def test_project_recalculate_one_task(self):
        self._project_recalculate(
            1, project_dates_res['one_task'], res_t=task_dates_res)

    def test_project_recalculate_tasks(self):
        self._project_recalculate(
            total_tasks, project_dates_res['tasks'], res_t=task_dates_res)


class TestProjectProjectEnd(TestProjectProjectBegin):
    calculation_type = 'date_end'


class TestProjectProjectNone(base.BaseCase):
    def test_project_recalculate_exceptions(self):
        cases = (
            # name, calculation_type, date_start, date
            ('pj_0', False, False, False),
            ('pj_1', False, '2015-08-01', False),
            ('pj_2', False, False, '2015-08-01'),
            ('pj_3', False, '2015-08-01', '2015-08-01'),
            ('pj_4', 'date_begin', False, False),
            ('pj_5', 'date_begin', False, '2015-08-01'),
            ('pj_6', 'date_end', False, False),
            ('pj_7', 'date_end', '2015-08-01', False),
        )
        with self.assertRaises(Warning):
            for nt in [0, 1, 5]:
                for n, ct, sd, ed in cases:
                    project = self.project_create(n + '_%d' % nt, nt, {
                        'calculation_type': ct,
                        'date_start': sd,
                        'date': ed,
                    })
                    project.project_recalculate()
