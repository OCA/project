# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from collections import namedtuple
from datetime import datetime, time, timedelta
from functools import cmp_to_key
import logging
import math
import random

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

from odoo.addons.resource.models import resource as resource_model

_logger = logging.getLogger(__name__)


class ProjectTaskSchedulingWizard(models.TransientModel):
    """ Wizard to compute tasks scheduling proposals.

    It has:
    - date_start: date to start the schedule.
    - cooling_ratio: Selection field to determinate the cooling ratio used by
                    the Simulated Annealing algorithm.
    - task_option: Selection field used to fulfill the task list according to
        the fallowing:
            'Not finished tasks': All not finished tasks
            'Not scheduled tasks': Not scheduled tasks in the set of
                                    all not finished tasks
            'Customized task list': No task
    - task_ids: list of tasks to schedule
    - employee_ids: Computed field. Each employee of them is able to do at
                    least one task in task_ids

    intervals are used in several parts of the code. An interval is a named
    tuple defined in the class ResourceCalendar in the file
    resource/models/resource.py of the odoo core module 'resource', see that
    file for further information.

    _state_obj is an attribute of this class too, used to create a Named tuple
    that contain a state. State is a tasks scheduling. It contains the
    following fields:
        - list tasks_list: list of task in specific order.
        - dict employees_dict: It stores a list of gaps for each employee.
                            Employee ids are the keys of the
                            dictionary and for each key is stored a list of
                            intervals (gaps). The intervals are ordered by
                            start_datetime ascendant and there is no overlap.
        - dict tasks_dict: It stores the assignation of each task. Task ids
                        are the keys and for each key is stored an interval.

    A gap is an interval that indicates a range of contiguous working intervals
    without task assigned and it is delimited by start and end datetime.

    _accum_inter is an attribute of this class, it is a dictionary. Employee
    ids are the keys and for each key is stored a list of intervals. Those are
    all working intervals of the employee necessary to do all task.

    To determinate the proposals of scheduling the method simulated_annealing
    is called. It implements a simulated annealing algorithm and return a
    list of _state_obj.

    """

    _name = "project.task.scheduling.wizard"
    _description = "Project task scheduling wizard"

    _state_obj = namedtuple('State', (
        'tasks_list',       # Priority list
        'tasks_dict',       # Assignation by task (schedule)
        'employees_dict',   # Free intervals by employee (gaps)
        'evaluation'        # Evaluation of the schedule
    ))
    _accum_inter = {}
    _employees_by_task = {}
    _MAX_HOURS_DELAYED = 1000000

    # fields
    # ------
    date_start = fields.Datetime(
        default=lambda self: self._default_start(),
        required=True,
    )
    cooling_ratio = fields.Selection(
        selection=[
            ('0.1', 'Fast (fast simulated annealing)'),
            ('0.5', 'Middle (middle simulated annealing)'),
            ('0.95', 'Slow (slow simulated annealing)'),
        ],
        string='Calculation speed',
        default='0.1',
        required=True,
        help="It is based on three thresholds that are included in the number "
             "of iterations for the search for solutions, with shorter times "
             "(fast) it's explored a smaller number of solutions, with longer "
             "(slow) greater chance of finding better solutions because of "
             "greater breadth of search."
    )
    task_option = fields.Selection(
        selection=[
            ('not_finished', 'Not finished tasks'),
            ('not_scheduled', 'Not scheduled tasks'),
            ('customized_list', 'Customized task list'),
        ],
        string="Task option",
        default='not_finished',
        required=True,
        help="The task list below is fulfilled depending on the option "
             "selected.\n"
             "Not finished tasks: All task out of closed stage and with "
             "progress < 100 %\n"
             "Not scheduled tasks: The subset of 'Not finished tasks' that "
             "has ending date not set\n"
             "Customized task list: No task"
    )
    task_ids = fields.Many2many(
        comodel_name='project.task',
        string="Tasks",
    )
    employee_ids = fields.Many2many(
        compute='_compute_employee_ids',
        comodel_name='hr.employee',
    )

    # Default methods
    # ---------------
    @api.model
    def _default_start(self):
        return fields.Datetime.now()

    # Compute methods
    # ---------------
    @api.multi
    @api.depends('task_ids.employee_scheduling_ids')
    def _compute_employee_ids(self):
        self.ensure_one()
        self.employee_ids = self.task_ids.mapped('employee_scheduling_ids')

    # Onchange methods
    # ----------------
    @api.onchange('task_option')
    def _onchange_task_option(self):
        domain = [('closed', '=', False), ('progress', '<', 100)]
        if self.task_option == 'not_finished':
            self.task_ids = self.env['project.task'].search(domain)
        elif self.task_option == 'not_scheduled':
            domain += [('date_end', '=', False)]
            self.task_ids = self.env['project.task'].search(domain)
        else:
            self.task_ids = False

    # Action methods
    # --------------
    @api.multi
    def action_accept(self):
        self.ensure_one()

        if not self.task_ids:
            raise ValidationError(_('Task list should not be empty'))

        closed_task = self.task_ids.filtered(
            lambda r: r.closed or r.progress >= 100)
        self.task_ids = self.task_ids - closed_task

        if len(self.task_ids) == 1:
            states = [self._get_init_state()]
        else:
            # Call main method to obtain a feasible schedule
            cooling_ratio = float(self.cooling_ratio)
            states = self.simulated_annealing(cooling_ratio=cooling_ratio)

        self.env['project.task.scheduling.proposal'].search([]).unlink()
        for state in states:
            ns_task_ids = closed_task.ids
            for task in state.tasks_list:
                if task.id not in state.tasks_dict:
                    ns_task_ids.append(task.id)
            proposal = self.env['project.task.scheduling.proposal'].create({
                'date_start': self.date_start,
                'evaluation': state.evaluation,
                'not_scheduled_task_ids': [[6, 0, ns_task_ids]]
            })
            for task_id, task_interval in state.tasks_dict.items():
                self.env['project.task.scheduling'].create({
                    'proposal_id': proposal.id,
                    'employee_id': task_interval.data['employee'].id,
                    'task_id': task_id,
                    'datetime_start': task_interval.start_datetime,
                    'datetime_stop': task_interval.end_datetime,
                })

        act = self.env['ir.actions.act_window']
        return act.for_xml_id("project_task_scheduling",
                              'project_task_scheduling_proposal_action')

    # Business methods
    # ----------------

    @api.multi
    def _get_total_tasks_hours(self):
        self.ensure_one()
        return sum(self.task_ids.mapped('remaining_hours'))

    @api.multi
    def _get_assigned_tasks(self):
        self.ensure_one()
        tasks = self.env['project.task']
        domain = [
            ('date_end', '>', self.date_start),
            ('employee_id', 'in', self.employee_ids.ids),
            ('id', 'not in', self.task_ids.ids),
        ]
        return tasks.search(domain, order='date_end')

    @api.multi
    def _init_employees_by_task(self):
        self.ensure_one()

        req_dict = dict()
        for task in self.task_ids:
            employee_scheduling = task.employee_scheduling_ids
            emp_len = len(employee_scheduling)
            for emp in employee_scheduling:
                req_dict.setdefault(emp.id, 10000)
                req_dict[emp.id] = min(req_dict[emp.id], emp_len)

        for task in self.task_ids:
            employees = task.employee_scheduling_ids
            employees = employees.sorted(lambda r: req_dict[r.id], True)
            self._employees_by_task[task.id] = employees

    @api.multi
    def _init_accum_inter(self):
        """
        Set _accum_inter attribute as a dictionary that store several working
        intervals by employee. The intervals are ordered by start_datetime
        ascendant and each one contain the accumulative working time from the
        first interval. This attribute is used to make a fast calculation of
        the working hours between two working intervals.
        """
        self.ensure_one()

        self._accum_inter = dict()

        tasks = self._get_assigned_tasks()
        total_hours = sum(self.task_ids.mapped('remaining_hours'))
        total_hours += sum(tasks.mapped('remaining_hours'))

        date_start = fields.Datetime.from_string(self.date_start)

        max_start = date_start
        for task in self.task_ids:
            task_date_start = fields.Datetime.from_string(task.date_start)
            max_start = max(max_start, task_date_start)

        for emp in self.employee_ids:
            tz_ctx = dict(tz=emp.resource_id.user_id.tz or self.env.user.tz)

            calendar = emp.resource_calendar_id.with_context(tz_ctx)
            user = self.env.user.with_context(tz_ctx)
            day_dt_tz = resource_model.to_naive_user_tz(date_start, user)
            current_dt = day_dt_tz

            hours = 0
            success = False
            while not success:
                intervals = calendar._get_day_work_intervals(
                    current_dt.date(),
                    current_dt.time(),
                    compute_leaves=True,
                    resource_id=emp.resource_id.id
                )
                for inter in intervals:
                    down = 0
                    if emp.id in self._accum_inter:
                        down = self._accum_inter[emp.id][-1].data['accum_up']
                    up = down + (inter[1] - inter[0]).total_seconds() / 3600

                    inter.data.update(accum_down=down, accum_up=up)
                    self._accum_inter.setdefault(emp.id, []).append(inter)

                    if max_start < inter.end_datetime:
                        if hours == 0:
                            hours_td = (inter[1] - max(max_start, inter[0]))
                            hours = hours_td.total_seconds() / 3600
                        else:
                            hours += (up - down)

                    if hours >= total_hours:
                        success = True
                        break

                # get next day
                next_work_day = calendar._get_next_work_day(current_dt)
                current_dt = datetime.combine(next_work_day, time())

    @api.multi
    def _get_sorted_tasks(self):
        """
        It's called from _get_init_state method to obtain a list of
        project.task() in a specific order.

        :return: list of project.task()
        """
        self.ensure_one()

        def task_cmp(a, b):
            a_date_deadline = fields.Date.from_string(a.date_deadline)
            b_date_deadline = fields.Date.from_string(b.date_deadline)
            if a_date_deadline and not b_date_deadline:
                return -1
            if b_date_deadline and not a_date_deadline:
                return 1
            if a_date_deadline and b_date_deadline:
                if a_date_deadline < b_date_deadline:
                    return -1
                if a_date_deadline > b_date_deadline:
                    return 1
            if a.priority != b.priority:
                return int(b.priority) - int(a.priority)
            return a.id - b.id

        result = self.task_ids.filtered(lambda r: not r.depending_task_ids)
        result = sorted(result, key=cmp_to_key(task_cmp))

        index = len(result) - 1
        while index >= 0:
            for dep in result[index].dependency_task_ids:
                if dep in result:
                    dep_index = result.index(dep)
                    if dep_index > index:
                        result.pop(dep_index)
                    else:   # pragma: no cover
                        continue
                index2 = index - 1
                while index2 >= 0 and task_cmp(dep, result[index2]) == -1:
                    index2 -= 1
                result.insert(index2 + 1, dep)
                index += 1
            index -= 1

        return result

    def _get_inteval_duration(self, interval):
        """ Determine the working hours at a given interval.
        _accum_inter attribute is used for the calculation.

        :param _interval_obj interval: interval

        :return: float: amount of hours
        """
        employee = interval.data['employee']
        emp_accum = self._accum_inter[employee.id]

        # right remainder
        pos_to = interval.data['pos_to']
        right_rem = emp_accum[pos_to].end_datetime - interval.end_datetime
        right_rem = right_rem.total_seconds() / 3600

        # left remainder
        pos_from = interval.data['pos_from']
        left_rem = interval.start_datetime - emp_accum[pos_from].start_datetime
        left_rem = left_rem.total_seconds() / 3600

        up = emp_accum[pos_to].data['accum_up']
        down = emp_accum[pos_from].data['accum_down']

        return up - down - right_rem - left_rem

    def _gap_remove_interval(self, gaps, gap_pos, inter_dst):
        """ Remove an interval from a gap of some employee.

        :param _interval_obj inter_dst: interval to remove

        :return: integer: pos of the gap next to the gap argument after removal
        """
        calendar = self.env['resource.calendar']

        start = inter_dst.start_datetime
        stop = inter_dst.end_datetime
        pos_from = inter_dst.data['pos_from']
        pos_to = inter_dst.data['pos_to']
        employee = inter_dst.data['employee']

        emp_accum = self._accum_inter[employee.id]

        gap = gaps[gap_pos]
        del gaps[gap_pos]

        # set left gap
        if gap.start_datetime < start:
            new_pos_to, new_stop = pos_from, start
            if start == emp_accum[pos_from].start_datetime:
                new_pos_to = pos_from - 1
                new_stop = emp_accum[pos_from - 1].end_datetime
            data = {
                'pos_from': gap.data['pos_from'],
                'pos_to': new_pos_to,
                'employee': employee,
            }
            inteval = calendar._interval_new(gap[0], new_stop, data)
            inteval.data['duration'] = self._get_inteval_duration(inteval)
            gaps.insert(gap_pos, inteval)
            gap_pos += 1

        # set right gap
        if stop < gap.end_datetime:
            new_pos_from, new_start = pos_to, stop
            if stop == emp_accum[pos_to].end_datetime:
                new_pos_from = pos_to + 1
                new_start = emp_accum[pos_to + 1].start_datetime
            data = {
                'pos_from': new_pos_from,
                'pos_to': gap.data['pos_to'],
                'employee': employee,
            }
            inteval = calendar._interval_new(new_start, gap[1], data)
            inteval.data['duration'] = self._get_inteval_duration(inteval)
            gaps.insert(gap_pos, inteval)
            gap_pos += 1

        return gap_pos

    def _gaps_remove_interval(self, gaps, inter_dst):
        """ Remove an interval from all gaps of an employee.

        :param _interval_obj inter_dst: interval to remove
        """

        calendar = self.env['resource.calendar']
        start_arg = inter_dst.start_datetime
        stop_arg = inter_dst.end_datetime
        employee = inter_dst.data['employee']

        emp_accum = self._accum_inter[employee.id]

        gap_pos = 0
        while gap_pos < len(gaps):
            gap = gaps[gap_pos]
            if gap.end_datetime <= start_arg:   # pragma: no cover
                gap_pos += 1
                continue
            if stop_arg <= gap.start_datetime:  # pragma: no cover
                break
            if start_arg < gap.end_datetime:
                data = {'employee': employee}
                # find left side of the interval to remove
                for pos in range(gap.data['pos_from'], gap.data['pos_to'] + 1):
                    curr_inter = emp_accum[pos]
                    if start_arg < curr_inter.end_datetime:
                        start = max(start_arg, curr_inter[0], gap[0])
                        data['pos_from'] = pos
                        break
                # find left side of the interval to remove
                for pos in range(gap.data['pos_to'], data['pos_from'] - 1, -1):
                    curr_inter = emp_accum[pos]
                    if curr_inter.start_datetime < stop_arg:
                        stop = min(stop_arg, curr_inter[1], gap[1])
                        data['pos_to'] = pos
                        to_remove = calendar._interval_new(start, stop, data)
                        break
                gap_pos = self._gap_remove_interval(gaps, gap_pos, to_remove)

    def _get_employees_dict(self):
        """
        It's called from _get_init_state method to obtain a list of gaps for
        each employee based on _accum_inter attribute and the tasks that have
        been assigned previously by other way, and they are in the
        planning horizon

        :return: dict: list of gaps for each employee
        """
        calendar = self.env['resource.calendar']

        employees_dict = dict()
        for emp in self.employee_ids:
            emp_accum = self._accum_inter[emp.id]
            len_acum = len(emp_accum)
            if len_acum:
                i_start = emp_accum[0]
                i_stop = emp_accum[-1]
                dur = i_stop.data['accum_up'] - i_start.data['accum_down']
                data = {'pos_from': 0, 'pos_to': len_acum - 1, 'duration': dur}
                inteval = calendar._interval_new(i_start[0], i_stop[1], data)
                employees_dict[emp.id] = [inteval]

        tasks = self._get_assigned_tasks()
        for task in tasks:
            gaps = employees_dict[task.employee_id.id]
            start = fields.Datetime.from_string(task.date_start)
            stop = fields.Datetime.from_string(task.date_end)
            data = {'employee': task.employee_id}
            to_remove = calendar._interval_new(start, stop, data)
            self._gaps_remove_interval(gaps, to_remove)

        return employees_dict

    def _obj_func(self, state):
        """ It's called from simulated_annealing method to evaluate a state

        :param _state_obj state: state

        :return: float: evaluation of state
        """
        total_hours_dy = task_dy_count = 0
        for interval in state.tasks_dict.values():
            task = interval.data['task']
            deadline = fields.Date.from_string(task.date_deadline)
            if deadline:
                deadline_dt = datetime.combine(deadline, time.max)
                delayed_td = (interval.end_datetime - deadline_dt)
                total_hours_dy += delayed_td.total_seconds() / 3600
                is_delayed = interval.data.get('delayed', False)
                task_dy_count += 1 if is_delayed else 0

        if abs(total_hours_dy) > self._MAX_HOURS_DELAYED:
            raise ValidationError(_(
                'Maybe some tasks have a very long "Initially Planned Hours" '
                'or Date start is far from the deadline of some tasks'))

        total_hours_dy += self._MAX_HOURS_DELAYED
        return task_dy_count * self._MAX_HOURS_DELAYED * 2 + total_hours_dy

    def _duplicate_interval(self, interval):
        """ Make a copy of an interval

        :param _interval_obj interval: interval to be duplicated
        :return: an interval (_interval_obj, see class docstring)
        """
        start = interval.start_datetime
        end = interval.end_datetime
        data = dict(interval.data)
        return self.env['resource.calendar']._interval_new(start, end, data)

    def _state_copy(self, state):
        """ Make a copy of a state

        :param _state_obj state: state to be copied
        :return: a _state_obj
        """
        tasks_list = list(state.tasks_list)

        tasks_dict = {}
        for key, interval in state.tasks_dict.items():
            tasks_dict[key] = self._duplicate_interval(interval)

        employees_dict = {}
        for key, gap_list in state.employees_dict.items():
            employees_dict[key] = gap_list[:]

        return self._state_obj(tasks_list, tasks_dict, employees_dict,
                               state.evaluation)

    def _get_interval(self, task_hours, gap, employee, start_arg):
        """ Determine the interval required by a given employee to do a task

        :param float task_hours: planned hours of the task
        :param hr.employee() employee: employee that has a calendar used to
                                        determinate the interval required
        :param datetime start: minimum datetime

        :return: an interval (_interval_obj, see class docstring)
        """
        calendar = self.env['resource.calendar']
        emp_accum = self._accum_inter[employee.id]

        if task_hours > gap.data['duration']:   # pragma: no cover
            return False

        start = False
        for pos in range(gap.data['pos_from'], gap.data['pos_to'] + 1):
            curr_inteval = emp_accum[pos]
            if curr_inteval.end_datetime > start_arg:
                inter_from = curr_inteval
                pos_from = pos
                start = max([start_arg, inter_from[0], gap[0]])
                diff_td = curr_inteval.end_datetime - start
                diff_hours = diff_td.total_seconds() / 3600
                break

        if not start:   # pragma: no cover
            return False

        for pos in range(pos_from, gap.data['pos_to'] + 1):
            curr_inteval = emp_accum[pos]
            hours = curr_inteval.data['accum_up'] - inter_from.data['accum_up']
            if curr_inteval.end_datetime > gap.end_datetime:
                hours_dt = (curr_inteval.end_datetime - gap.end_datetime)
                hours -= hours_dt.total_seconds() / 3600
            hours += diff_hours
            if hours >= task_hours:
                remainder = timedelta(hours=hours - task_hours)
                stop = min(curr_inteval[1], gap[1]) - remainder
                data = dict(pos_from=pos_from, pos_to=pos)
                return calendar._interval_new(start, stop, data)

        return False    # pragma: no cover

    def _get_assignment(self, state, task, employee, start, best_end):
        """
        Determine the earliest possible interval to assign a task to an
        employee

        :param _state_obj state: a scheduling
        :param project.task() task: task to be assigned
        :param hr.employee() employee: employee
        :param datetime start_arg: the earliest start datetime
        :param datetime best_end: the lastest end datetime

        :return: a tuple (interval, pos)
                This interval belong to the gap at pos 'pos' in the gaps list
                of the employee
        """
        task_hours = task.remaining_hours

        gaps = state.employees_dict[employee.id]
        for pos in range(len(gaps)):
            gap = gaps[pos]
            if best_end - timedelta(hours=task.remaining_hours) < gap[0]:
                break
            if start < gap.end_datetime:
                interval = self._get_interval(task_hours, gap, employee, start)
                if interval:
                    return interval, pos
        return False, False

    def _get_earliest_start(self, state, task):
        """
        Get the earliest possible start datetime to start the task depending
        on date_start of the wizard, date_start of the task and the latest
        end assignation datetime of the predecessors.

        :param _state_obj state: state
        :param project.task() task: task
        :return: datetime:
        """

        start = fields.Datetime.from_string(self.date_start)
        if task.date_start and not task.date_end:
            task_start = fields.Datetime.from_string(task.date_start)
            start = max(start, task_start)
        for depend in task.dependency_task_ids:
            if depend.id in state.tasks_dict:
                end_datetime = state.tasks_dict[depend.id].end_datetime
            else:
                end_datetime = depend.date_end
                end_datetime = fields.Datetime.from_string(end_datetime)
            if not end_datetime:
                return False
            start = max(end_datetime, start)
        return start

    def _greedy_distribution(self, state, init_index=0):
        """
        It's called from _get_init_state and _generate_neighbor methods
        to assign self.tasks to the employees using a greedy strategy base on
        the serial scheduling scheme

        :param _state_obj state: state
        :param init_index: the tasks in position >= init_index will be
                            scheduled
        :return: _state_obj
        """
        date_start = fields.Datetime.from_string(self.date_start)
        distant_datetime = date_start + timedelta(weeks=520)
        for task in state.tasks_list[init_index:]:
            start = self._get_earliest_start(state, task)
            if not start:
                break
            best_interval, best_gap_pos = False, False
            best_end_datetime = distant_datetime
            for employee in self._employees_by_task[task.id]:
                interval, pos = self._get_assignment(state, task, employee,
                                                     start, best_end_datetime)
                if interval and interval.end_datetime < best_end_datetime:
                    best_interval = interval
                    best_interval.data.update(employee=employee)
                    best_end_datetime = best_interval.end_datetime
                    best_gap_pos = pos

            if best_interval:
                data = dict(task=task, duration=task.remaining_hours)
                if task.date_deadline:
                    end_date = best_interval.end_datetime.date()
                    deadline = fields.Date.from_string(task.date_deadline)
                    data.update(delayed=end_date > deadline)
                best_interval.data.update(data)
                state.tasks_dict[task.id] = best_interval

                employee = best_interval.data['employee']
                gaps = state.employees_dict[employee.id]
                self._gap_remove_interval(gaps, best_gap_pos, best_interval)

        return state

    def _add_gap(self, gaps, interval):
        """ Add a new gap to the list of gaps of some employee

        :param _interval_obj gaps: list of gaps
        :param _interval_obj interval: interval to insert as a new gap in gaps
                                        list passed as an argument.
                                        the employee is specified in 'data'
                                        field of the interval
        """
        emp_accum = self._accum_inter[interval.data['employee'].id]

        pos = 0
        while pos < len(gaps) and gaps[pos][0] < interval[1]:
            pos += 1
        gaps.insert(pos, interval)

        def merge_right(index):
            l_gap, r_gap = gaps[index], gaps[index + 1]
            merge = False
            if l_gap.data['pos_to'] == r_gap.data['pos_from']:
                if l_gap.end_datetime == r_gap.start_datetime:
                    merge = True
            elif l_gap.data['pos_to'] + 1 == r_gap.data['pos_from']:
                if l_gap[1] == emp_accum[l_gap.data['pos_to']][1] \
                        and r_gap[0] == emp_accum[r_gap.data['pos_from']][0]:
                    merge = True
            if merge:
                gaps[index] = l_gap._replace(end_datetime=r_gap.end_datetime)
                gaps[index].data['pos_to'] = r_gap.data['pos_to']
                gaps[index].data['duration'] += r_gap.data['duration']
                del gaps[index + 1]
            return merge

        # Left join
        if pos and merge_right(pos - 1):
            pos -= 1
        if pos < len(gaps) - 1:
            merge_right(pos)

    def _generate_neighbor(self, state, pos_arg=False):
        """ Compute a neighbor of a state

        It's called from simulated_annealing method to get a neighbor from a
        given state.

        :param _state_obj state: state
        :param int pos_arg: It is used for testing purpose

        :return: a _state_obj
        """
        new_state = self._state_copy(state)
        tasks_list = new_state.tasks_list
        tasks_dict = new_state.tasks_dict
        employees_dict = new_state.employees_dict

        # pos_arg is used for testing purpose
        pos = pos_arg or random.randrange(len(tasks_list) - 1)
        if tasks_list[pos] in tasks_list[pos + 1].dependency_task_ids:
            return False

        # swap
        temp = tasks_list[pos]
        tasks_list[pos] = tasks_list[pos + 1]
        tasks_list[pos + 1] = temp

        # delete task in pos and after pos
        for task in tasks_list[pos:]:
            if task.id in tasks_dict:
                interval = tasks_dict[task.id]
                gaps = employees_dict[interval.data['employee'].id]
                self._add_gap(gaps, interval)
                del tasks_dict[task.id]

        return self._greedy_distribution(state=new_state, init_index=pos)

    def _get_init_state(self):
        """ Compute the first scheduling

        It's called from simulated_annealing method to get the first state.

        :return: a _state_obj that represent the first scheduling
        """

        # Initialize _accum_inter attribute of this class
        self._init_accum_inter()
        # Initialize _employees_by_task attribute of this class
        self._init_employees_by_task()

        tasks_list = self._get_sorted_tasks()
        employees_dict = self._get_employees_dict()
        tasks_dict = dict()
        state = self._state_obj(tasks_list, tasks_dict, employees_dict, False)

        return self._greedy_distribution(state)

    def _print_summary(self, states_list, current_duration, max_duration,
                       it_count, iterations):
        """ Print summary of the simulated_annealing method execution """

        _logger.info('********** SUMMARY **********')

        improvements = len(states_list) - 1
        _logger.info('improvements: %(imp)d' % {'imp': improvements})

        duration = current_duration.total_seconds()
        _logger.info('Duration: %(duration)f' % {'duration': duration})

        if current_duration >= max_duration:
            _logger.info("Execution time >= maximum time")

        it_count *= iterations
        _logger.info('Number of iterations: %(it)d' % {'it': it_count})

        _logger.info('*****************************')

    def simulated_annealing(self, init_temp=100000000, final_temp=0.1,
                            iterations=10, cooling_ratio=0.1,
                            limit_seconds=600):
        """ Main method to compute the scheduling proposals

        :param float init_temp: initial temperature
        :param float final_temp: final temperature
        :param int iterations: the number of steps to reach the equilibrium
        :param float cooling_ratio: cooling ratio. The algorithm decreases the
                                    value of temperature multiplying it by
                                    the cooling ratio
        :param int limit_seconds: Max duration of the algorithm (in seconds)

        :return: list of _state_obj (for further information about _state_obj,
                see docstring of the class)

        """
        init_time = datetime.now()
        max_duration = timedelta(seconds=limit_seconds)
        current_duration = timedelta()
        it_count = 0
        temp = init_temp

        states_list = []

        st = self._get_init_state()
        best_eval = eval_st = round(self._obj_func(st), 10)
        states_list.append(st._replace(evaluation=best_eval))

        while temp >= final_temp and current_duration < max_duration:
            for it in range(iterations):
                st_neighbor = self._generate_neighbor(st)
                if not st_neighbor:
                    continue
                it_count += 1
                eval_st_neighbor = round(self._obj_func(st_neighbor), 10)
                eval_diff = eval_st_neighbor - eval_st
                if eval_diff < 0:
                    st = st_neighbor
                    eval_st = eval_st_neighbor
                    if eval_st < best_eval:
                        best_eval = eval_st
                        states_list.append(st._replace(evaluation=best_eval))
                else:
                    if random.random() < math.exp(-(eval_diff / temp)):
                        st = st_neighbor
                        eval_st = eval_st_neighbor
                current_duration = datetime.now() - init_time
                if current_duration > max_duration:
                    break
            temp *= cooling_ratio
            _logger.info('Current temperature: %(temp)f' % {'temp': temp})

        self._print_summary(states_list, current_duration, max_duration,
                            it_count, iterations)
        return states_list
