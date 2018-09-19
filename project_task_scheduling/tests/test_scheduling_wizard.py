# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from collections import namedtuple
from datetime import date, datetime, time, timedelta

from odoo import fields
from odoo.exceptions import ValidationError

from odoo.addons.project_task_scheduling.tests.common import \
    TestSchedulingCommon


class TestSchedulingWizard(TestSchedulingCommon):

    def test_project_employees(self):
        """ test self.jth_emp and self.root_emp are all employees in the
        project """
        self.assertEqual(self.restricted_project.employee_ids,
                         self.jth_emp + self.root_emp)

    def test_project_tasks(self):
        """ test self.task_3, self.task_2, self.task_7, self.task_1 are all
        tasks in the project """
        self.assertEqual(self.restricted_project.task_ids,
                         self.task_3 + self.task_2 + self.task_7 + self.task_1)

    def test_wizard_tasks(self):
        """ test self.task_3, self.task_2, self.task_7, self.task_1 are all
        tasks in self.wizard for scheduling """
        self.assertEqual(self.wizard.task_ids,
                         self.task_3 + self.task_2 + self.task_7 + self.task_1)

    def test_onchange_task_option(self):
        """ test onchange_task_option method set the correct tasks in task_ids
        attribute of self.wizard """
        with self.env.do_in_onchange():
            self.wizard.task_option = 'not_finished'
            self.wizard._onchange_task_option()
            domain = [('closed', '!=', True), ('progress', '<', 100)]
            self.assertEqual(self.wizard.task_ids,
                             self.env['project.task'].search(domain))

            self.wizard.task_option = 'not_scheduled'
            self.wizard._onchange_task_option()
            domain = [('closed', '!=', True), ('progress', '<', 100),
                      ('scheduled', '!=', True)]
            self.assertEqual(self.wizard.task_ids,
                             self.env['project.task'].search(domain))

            self.wizard.task_option = 'customized_list'
            self.wizard._onchange_task_option()
            self.assertEqual(len(self.wizard.task_ids), 0)

    def test_get_total_tasks_hours(self):
        self.assertEqual(self.wizard._get_total_tasks_hours(), 13)

    def test_get_sorted_tasks(self):
        """ test self.wizard._get_sorted_tasks returns a task list in correct
        order """
        expected_list = [self.task_2, self.task_3, self.task_7, self.task_1]
        self.assertEqual(self.wizard._get_sorted_tasks(), expected_list)

    def test_get_employees_dict(self):
        """ Test self.wizard._get_employee_dicts return a dict with one
        interval by employee """
        employees_dict = self.wizard._get_employees_dict()

        self.assertEqual(len(employees_dict.keys()), 2)
        for value in employees_dict.values():
            self.assertEqual(len(value), 1)

    def test_get_employees_dict_with_values(self):
        task_obj = self.env['project.task']
        assigned_task = task_obj.browse(self.ref("project.project_task_1"))
        date_start = fields.Datetime.from_string(self.wizard.date_start)
        a_start = datetime.combine(date_start, time(13))
        a_end = datetime.combine(date_start, time(17))

        assigned_task.write({
            'employee_id': self.jth_emp.id,
            'date_start': a_start,
            'date_end': a_end,
        })

        accum_emp = self.wizard._accum_inter[self.jth_emp.id]

        emp_dict = self.wizard._get_employees_dict()
        emp_gaps = emp_dict[self.jth_emp.id]

        self.assertEqual(len(emp_gaps), 2)

        self.assertEqual(emp_gaps[0][0], accum_emp[0][0])
        self.assertEqual(emp_gaps[0][1], accum_emp[0][1])

        self.assertEqual(emp_gaps[1][0], accum_emp[2][0])
        self.assertEqual(emp_gaps[1][1], accum_emp[-1][1])

    def test_get_init_state(self):
        init_state = self.wizard._get_init_state()

        # Assignations in state returned by _get_init_state are the followings:
        # day1: date_start
        # day2: Next work day to day1
        # is delayed: assignation end date > date_deadline of task
        #
        # self.task_2: (day1 8:00 - day1 10:00 - self.jth_emp)
        # self.task_1: (day2 10:00 - day2 11:00 - self.jth_emp) [is delayed]
        #
        # self.task_3: (day1 8:00 - day1 11:00 - self.root_emp)
        # self.task_7: (day1 11:00 - day2 10:00 - self.root_emp) [is delayed]
        calendar = self.root_emp.resource_id.calendar_id
        day1 = fields.Datetime.from_string(self.wizard.date_start)
        day2 = calendar._get_next_work_day(day1)

        data_check_dict = {
            self.task_2.id: (datetime.combine(day1, time(8)),
                             datetime.combine(day1, time(10)),
                             self.jth_emp),
            self.task_1.id: (datetime.combine(day2, time(10)),
                             datetime.combine(day2, time(11)),
                             self.jth_emp),
            self.task_3.id: (datetime.combine(day1, time(8)),
                             datetime.combine(day1, time(11)),
                             self.root_emp),
            self.task_7.id: (datetime.combine(day1, time(11)),
                             datetime.combine(day2, time(10)),
                             self.root_emp),
        }
        for task_id, data_check in data_check_dict.items():
            assigment = init_state.tasks_dict[task_id]
            self.assertEqual(assigment.start_datetime, data_check[0])
            self.assertEqual(assigment.end_datetime, data_check[1])
            self.assertEqual(assigment.data['employee'], data_check[2])

    def test_obj_func(self):
        max_hours_delayed = self.wizard._MAX_HOURS_DELAYED

        # evaluate initial state
        init_state = self.wizard._get_init_state()
        evaluation = self.wizard._obj_func(init_state)

        # two tasks are scheduled after their date_deadline
        # (self.task_7 and self.task_1) see test_get_init_state_1 method
        task_dy_count = 2

        # total_hours_dy total delayed hours of all tasks
        total_hours_dy = 0
        for interval in init_state.tasks_dict.values():
            task = interval.data['task']
            deadline = fields.Date.from_string(task.date_deadline)
            deadline_dt = datetime.combine(deadline, time.max)
            delayed_td = (interval.end_datetime - deadline_dt)
            total_hours_dy += delayed_td.total_seconds() / 3600.0

        total_hours_dy += max_hours_delayed
        expected_eval = task_dy_count * max_hours_delayed * 2 + total_hours_dy

        self.assertEqual(evaluation, expected_eval)

    def test_obj_func_fail(self):
        date_start = fields.Datetime.from_string(self.wizard.date_start)
        date_deadline = date_start + timedelta(days=50000)
        self.task_2.write({'date_deadline': date_deadline})
        state = self.wizard._get_init_state()
        with self.assertRaises(ValidationError):
            self.wizard._obj_func(state)

    def test_generate_neighbor_false(self):
        init_st = self.wizard._get_init_state()
        neighbor_st = self.wizard._generate_neighbor(init_st, pos_arg=2)
        self.assertFalse(neighbor_st)

    def test_generate_neighbor_pos_arg_1(self):
        init_st = self.wizard._get_init_state()
        neighbor_st = self.wizard._generate_neighbor(init_st, pos_arg=1)

        expected_list = [self.task_2, self.task_7, self.task_3, self.task_1]
        self.assertEqual(neighbor_st.tasks_list, expected_list)

        # Assignations in neighbor_st returned by _generate_neighbor are the
        # followings:
        # is delayed: assignation end date > date_deadline of task
        #
        # self.task_2: (8:00 - 10:00 - self.jth_emp)    [Not delayed]
        # self.task_3: (10:00 - 14:00 - self.jth_emp)   [Not delayed]
        # self.task_1: (16:00 - 17:00 - self.jth_emp)   [Not delayed]
        #
        # self.task_7: (8:00 - 16:00 - self.root_emp)   [Not delayed]
        date_start = fields.Datetime.from_string(self.wizard.date_start)
        data_check_dict = {
            self.task_2.id: (datetime.combine(date_start, time(8)),
                             datetime.combine(date_start, time(10)),
                             self.jth_emp),
            self.task_3.id: (datetime.combine(date_start, time(10)),
                             datetime.combine(date_start, time(14)),
                             self.jth_emp),
            self.task_1.id: (datetime.combine(date_start, time(16)),
                             datetime.combine(date_start, time(17)),
                             self.jth_emp),
            self.task_7.id: (datetime.combine(date_start, time(8)),
                             datetime.combine(date_start, time(16)),
                             self.root_emp),
        }
        for task_id, data_check in data_check_dict.items():
            assigment = neighbor_st.tasks_dict[task_id]
            self.assertEqual(assigment.start_datetime, data_check[0])
            self.assertEqual(assigment.end_datetime, data_check[1])
            self.assertEqual(assigment.data['employee'], data_check[2])

    def test_generate_neighbor_pos_arg_1_is_better_than_start_state(self):
        init_st = self.wizard._get_init_state()
        eval_init_st = round(self.wizard._obj_func(init_st), 10)

        neighbor_st = self.wizard._generate_neighbor(init_st, pos_arg=1)
        eval_neighbor_st = round(self.wizard._obj_func(neighbor_st), 10)

        self.assertLess(eval_neighbor_st, eval_init_st)

    def test_simulated_annealing_can_improve_initial_state(self):
        init_state = self.wizard._get_init_state()
        eval_init_st = round(self.wizard._obj_func(init_state), 10)

        cooling_ratio = float(self.wizard.cooling_ratio)
        sa_state = self.wizard.simulated_annealing(cooling_ratio=cooling_ratio)
        eval_sa_state = round(self.wizard._obj_func(sa_state[-1]), 10)

        self.assertLessEqual(eval_sa_state, eval_init_st)

    def test_simulated_annealing_with_limited_time(self):
        name = 'odoo.addons.project_task_scheduling.wizards.scheduling_wizard'

        with self.assertLogs(name) as cm:
            self.wizard.simulated_annealing(cooling_ratio=0.99,
                                            limit_seconds=1)
        log_msg = 'Execution time >= maximum time'
        self.assertIn('INFO:%(name)s:%(msg)s' % {'name': name, 'msg': log_msg},
                      cm.output)

    def test_simulated_annealing_several_tasks(self):
        """"""
        task_nt = namedtuple('Task', ('name', 'hours', 'dependencies',
                                      'deadline', 'priority'))
        tasks_list = [
            task_nt('F', 10, [], date(2018, 12, 5), '0'),
            task_nt('G', 10, ['F'], date(2018, 12, 1), '0'),
            task_nt('I', 10, ['G'], date(2018, 11, 30), '0'),
            task_nt('A', 10, [], date(2018, 12, 2), '0'),
            task_nt('J', 10, [], False, '0'),
            task_nt('B', 10, ['A'], date(2018, 12, 6), '0'),
            task_nt('C', 10, ['A'], date(2018, 12, 6), '0'),
            task_nt('D', 10, ['B', 'C'], date(2018, 12, 5), '0'),
            task_nt('E', 10, [], False, '0'),
            task_nt('H', 10, ['F', 'C', 'I'], date(2018, 12, 6), '0'),
            task_nt('K', 10, [], False, '1'),
        ]
        tasks_dict = {}
        task_ids = []
        task_obj = self.env['project.task']
        for task in tasks_list:
            dependencies = [tasks_dict[name].id for name in task.dependencies]
            new_task = task_obj.create({
                'name': task.name,
                'planned_hours': task.hours,
                'dependency_task_ids': [[6, 0, dependencies]],
                'date_deadline': task.deadline,
                'priority': task.priority,
            })
            tasks_dict[task.name] = new_task
            task_ids.append(new_task.id)

        self.wizard.write({'task_ids': [[6, 0, task_ids]]})
        tasks = self.wizard._get_sorted_tasks()
        self.assertEqual(len(tasks), len(tasks_list))

        cooling_ratio = float(self.wizard.cooling_ratio)
        self.wizard.simulated_annealing(cooling_ratio=cooling_ratio)

    def test_action_accept_without_tasks(self):
        with self.assertRaises(ValidationError):
            self.wizard.task_ids = False
            self.wizard.action_accept()

    def test_action_accept_with_one_tasks(self):
        self.wizard.task_ids = self.task_2
        self.wizard.action_accept()
        proposals = self.env['project.task.scheduling.proposal'].search([])
        self.assertEqual(len(proposals), 1)

    def test_action_accept(self):
        self.wizard.action_accept()
        proposals = self.env['project.task.scheduling.proposal'].search([])
        self.assertGreaterEqual(len(proposals), 1)

    def test_action_accept_with_task_not_scheduled(self):
        """ If some task can not be done by any employee, this task and its
        dependencies will not be scheduled """
        self.root_emp.category_ids = False
        self.wizard.action_accept()
        prop = self.env['project.task.scheduling.proposal'].search([], limit=1)
        self.assertIn(self.task_7, prop.not_scheduled_task_ids)
        self.assertIn(self.task_1, prop.not_scheduled_task_ids)
