# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp.exceptions import ValidationError
from . import base

n_projects = base.n_projects
project_date_cases = base.project_init_dates
total_tasks = base.n_tasks
task_dates_cases = base.task_dates
task_days_res = {
    'date_begin': {
        'pj_0': (
            # name, from_days, estimate_days
            ('task_0', -2, 5),
            ('task_1', 1, 1),  # ('task_1', 0, 1),
            ('task_2', 5, 11),
            ('task_3', 12, 20),
            ('task_4', 21, 2),
        ),
        'pj_1': (
            ('task_0', -2, 5),
            ('task_1', 1, 1),  # ('task_1', 0, 1),
            ('task_2', 5, 11),
            ('task_3', 12, 20),
            ('task_4', 21, 2),
        ),
        'pj_2': (
            ('task_0', -2, 5),
            ('task_1', 0, 1),
            ('task_2', 5, 11),
            ('task_3', 12, 20),
            ('task_4', 21, 2),
        ),
    },
    'date_end': {
        'pj_0': (
            # name, from_days, estimate_days
            ('task_0', 40, 5),
            ('task_1', 35, 11),
            ('task_2', 22, 20),
            ('task_3', 1, 1),  # ('task_3', 0, 1),
            ('task_4', -1, 2),
        ),
        'pj_1': (
            ('task_0', 40, 5),
            ('task_1', 35, 11),
            ('task_2', 22, 20),
            ('task_3', 1, 1),  # ('task_3', 0, 1),
            ('task_4', -1, 2),
        ),
        'pj_2': (
            ('task_0', 40, 5),
            ('task_1', 35, 11),
            ('task_2', 22, 20),
            ('task_3', 1, 1),  # ('task_3', 0, 1),
            ('task_4', -1, 2),
        ),
    },
}


# One test case per method
class TestProjectTaskBegin(base.BaseCase):
    calculation_type = 'date_begin'

    #######################################################################
    # Check _dates_onchange
    #   * with_context={'task_recalculate': True}
    def test_dates_onchange_when_recalculate(self):
        project = self.project_create('Test project', total_tasks, {
            'calculation_type': self.calculation_type,
            'date_start': '2015-08-01',
            'date': '2015-08-31',
        })
        task = project.tasks[0]
        vals = {
            'date_start': '2015-08-03 08:00:00',
            'date_end': '2015-08-14 18:00:00',
        }
        # Execute _dates_onchange with context: task_recalculate=True
        task_ctx = task.with_context(task.env.context, task_recalculate=True)
        vals = task_ctx._dates_onchange(vals)
        self.assertTrue('from_days' not in vals,
                        "FAIL: from_days assigned")
        self.assertTrue('estimated_days' not in vals,
                        "FAIL: estimated_days assigned")

    #######################################################################
    # Check _dates_onchange
    def test_dates_onchange(self):
        pc = 0
        for n, sd, ed in project_date_cases:
            # Prepare test case
            project = self.project_create(n, total_tasks, {
                'calculation_type': self.calculation_type,
                'date_start': sd,
                'date': ed,
            })

            tc = 0
            for i in range(0, total_tasks):
                dates = task_dates_cases[self.calculation_type][n][i]
                task = project.tasks.filtered(
                    lambda r: r.name == dates[0])
                vals = {
                    'date_start': '%s 08:00:00' % dates[1],
                    'date_end': '%s 18:00:00' % dates[2],
                }
                # Execute _dates_onchange
                vals = task._dates_onchange(vals)
                # Check test case
                days = task_days_res[self.calculation_type][n][i]
                self.assertEqual(
                    vals.get('from_days', False), days[1],
                    "[%d, %d] FAIL: from_days" % (pc, tc))
                self.assertEqual(
                    vals.get('estimated_days', False), days[2],
                    "[%d, %d] FAIL: estimated_days" % (pc, tc))
                tc += 1
            pc += 1


class TestProjectTaskEnd(TestProjectTaskBegin):
    calculation_type = 'date_end'


class TestProjectTask(base.BaseCase):

    #######################################################################
    # Check _estimated_days_check constraint
    #   * estimated_days > O: OK
    #   * estimated_days == 0: ValidationError
    #   * estimated_days < 0: ValidationError
    def test_estimated_days_check(self):
        error_cases = (
            # name, estimated_days
            ('task_0', -5),
            ('task_1', -1),
            ('task_2', 0),
        )
        ok_cases = (
            ('task_10', 1),
            ('task_11', 5),
            ('task_12', 100),
        )
        project = self.project_create('test', 0)
        # ValidationError cases
        with self.assertRaises(ValidationError):
            for n, ed in error_cases:
                self.project_task_add(project, n, {
                    'estimated_days': ed,
                })
        # OK cases
        for n, ed in ok_cases:
            self.project_task_add(project, n, {
                'estimated_days': ed,
            })
