# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. -
# Jordi Ballester Alomar
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models
from datetime import datetime
from datetime import timedelta
from dateutil.rrule import *
import openerp.addons.decimal_precision as dp


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'
    poc = fields.Float('% Completed')


class Project(models.Model):
    
    _inherit = "project.project"

    @staticmethod
    def _get_evm_ratios(ac, pv, ev, bac):

        res = {
            'ac': ac,
            'pv': pv,
            'ev': ev,
            'bac': bac,
        }

        # PCC: Costs to date / Total costs
        try:
            res['pcc'] = res['ac'] / res['pv']
        except ZeroDivisionError:
            res['pcc'] = 0

        # SV: Schedule variance
        res['sv'] = res['ev'] - res['pv']

        # SVP: Schedule variance in percentage
        try:
            res['svp'] = res['sv'] / res['pv']
        except ZeroDivisionError:
            res['svp'] = 0

        # SPI: Schedule Performance Index
        try:
            res['spi'] = res['ev'] / res['pv']
        except ZeroDivisionError:
            res['spi'] = 0

        # CV: Cost Variance
        res['cv'] = res['ev'] - res['ac']

        # CVP: Cost Variance Percent
        try:
            res['cvp'] = (res['cv'] / res['ev']) * 100
        except ZeroDivisionError:
            res['cvp'] = 0

        # CPI: Cost Performance Index
        try:
            res['cpi'] = res['ev'] / res['ac']
        except ZeroDivisionError:
            res['cpi'] = 1

        # TCPI: To-complete Performance Index
        bac_ac_amount = res['bac'] - res['ac']
        try:
            res['tcpi'] = (res['bac'] - res['ev']) / bac_ac_amount
        except ZeroDivisionError:
            res['tcpi'] = 1

        # EAC: Estimate at completion
        try:
            res['eac'] = res['bac'] / res['cpi']
        except ZeroDivisionError:
            res['eac'] = res['bac']

        # VAC: Variance at Completion
        res['vac'] = res['bac'] - res['eac']

        # VACP: Variance at Completion Percent
        try:
            res['vacp'] = (res['vac'] / res['bac']) * 100
        except ZeroDivisionError:
            res['vacp'] = 0

        # ETC: Estimate To Complete
        try:
            res['etc'] = (res['bac'] - res['ev']) / res['cpi']
        except ZeroDivisionError:
            res['etc'] = 0

        # EAC: Estimate At Completion
        try:
            res['eac'] = res['bac'] / res['cpi']
        except ZeroDivisionError:
            res['eac'] = 0

        # POC - Percent of Completion
        try:
            res['poc'] = res['ev'] / res['bac'] * 100
        except ZeroDivisionError:
            res['poc'] = 0

        return res

    def _get_earliest_latest_dates(self):
        project = self
        cr = self.env.cr
        # Get the earliest and latest dates for the associated tasks
        cr.execute("""SELECT MIN(date_start)
                   FROM project_task
                   WHERE project_id=%s""", (project.id, ))
        min_date_start = cr.fetchone()[0] or 0
        if min_date_start == 0:
            datetime_start = datetime.today()
        else:
            datetime_start = datetime.strptime(min_date_start,
                                               "%Y-%m-%d %H:%M:%S")

        cr.execute("""SELECT MAX(date_end)
                   FROM project_task
                   WHERE project_id=%s""", (project.id, ))
        max_date_end = cr.fetchone()[0] or 0
        if max_date_end == 0:
            datetime_end = datetime.today()
        else:
            datetime_end = datetime.strptime(max_date_end,
                                             "%Y-%m-%d %H:%M:%S")

        cr.execute("""SELECT MAX(date_last_stage_update)
                   FROM project_task
                   WHERE project_id=%s""", (project.id, ))
        max_date_end_2 = cr.fetchone()[0] or 0
        if max_date_end_2 == 0:
            datetime_end_2 = datetime.today()
        else:
            datetime_end_2 = datetime.strptime(max_date_end,
                                             "%Y-%m-%d %H:%M:%S")
        datetime_end = max(datetime_end, datetime_end_2)

        return datetime_start, datetime_end

    def _get_budget_at_completion(self):
        cr = self.env.cr
        # Compute the Budget at Completion
        cr.execute("""
        SELECT SUM(PT.planned_hours * ip.value_float)
        FROM project_task as PT
        INNER JOIN resource_resource RES
        ON RES.user_id = PT.user_id
        INNER JOIN hr_employee EMP
        ON EMP.resource_id = RES.id
        INNER JOIN product_product PR
        ON PR.id = EMP.product_id
        INNER JOIN product_template PRT
        ON PRT.id = PR.product_tmpl_id
        LEFT JOIN ir_property ip
        ON (ip.name='standard_price'
        AND ip.res_id=CONCAT('product.template,',PRT.id)
        AND ip.company_id=PT.company_id)
        WHERE PT.project_id = %s""", (self.id, ))
        res = cr.fetchone()
        if res:
            return res[0] or 0.0
        else:
            return 0.0

    def _get_plan_cost_to_date(self):
        cr = self.env.cr
        today = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        # Compute the Budget at Completion
        cr.execute("""
        SELECT SUM(PT.planned_hours * ip.value_float)
        FROM project_task as PT
        INNER JOIN resource_resource RES
        ON RES.user_id = PT.user_id
        INNER JOIN hr_employee EMP
        ON EMP.resource_id = RES.id
        INNER JOIN product_product PR
        ON PR.id = EMP.product_id
        INNER JOIN product_template PRT
        ON PRT.id = PR.product_tmpl_id
        LEFT JOIN ir_property ip
        ON (ip.name='standard_price'
        AND ip.res_id=CONCAT('product.template,',PRT.id)
        AND ip.company_id=PT.company_id)
        WHERE PT.project_id = %s
        AND PT.date_end <= %s""", (self.id, today))
        res = cr.fetchone()
        if res:
            return res[0] or 0.0
        else:
            return 0.0

    def _get_actual_cost_to_date(self):
        cr = self.env.cr
        # Compute the actual cost
        cr.execute("""
        SELECT SUM(PTW.hours * ip.value_float)
        FROM project_task_work AS PTW
        INNER JOIN project_task AS PT
        ON PTW.task_id = PT.id
        INNER JOIN resource_resource RES
        ON RES.user_id = PT.user_id
        INNER JOIN hr_employee EMP
        ON EMP.resource_id = RES.id
        INNER JOIN product_product PR
        ON PR.id = EMP.product_id
        INNER JOIN product_template PRT
        ON PRT.id = PR.product_tmpl_id
        LEFT JOIN ir_property ip
        ON (ip.name='standard_price'
        AND ip.res_id=CONCAT('product.template,',PRT.id)
        AND ip.company_id=PT.company_id)
        WHERE PT.project_id = %s""", (self.id, ))
        res = cr.fetchone()
        if res:
            return res[0] or 0.0
        else:
            return 0.0

    def _get_earned_value_to_date(self):
        cr = self.env.cr
        # Compute the earned value
        cr.execute("""
        SELECT SUM(PT.planned_hours * ip.value_float * PTT.poc/100)
        FROM project_task as PT
        INNER JOIN project_task_type as PTT
        ON PTT.id = PT.stage_id
        INNER JOIN resource_resource RES
        ON RES.user_id = PT.user_id
        INNER JOIN hr_employee EMP
        ON EMP.resource_id = RES.id
        INNER JOIN product_product PR
        ON PR.id = EMP.product_id
        INNER JOIN product_template PRT
        ON PRT.id = PR.product_tmpl_id
        LEFT JOIN ir_property ip
        ON (ip.name='standard_price'
        AND ip.res_id=CONCAT('product.template,',PRT.id)
        AND ip.company_id=PT.company_id)
        WHERE PT.project_id = %s""", (self.id, ))
        res = cr.fetchone()
        if res:
            return res[0] or 0.0
        else:
            return 0.0

    @api.one
    def _earned_value(self):
        # Compute the Budget at Completion
        bac = self._get_budget_at_completion()
        # Compute Planned Value
        pv = self._get_plan_cost_to_date()
        # Compute Actual Cost
        ac = self._get_actual_cost_to_date()
        # Compute Earned Value
        ev = self._get_earned_value_to_date()

        ratios = self._get_evm_ratios(ac, pv, ev, bac)
        for key in ratios.keys():
            self[key] = ratios[key]

    pv = fields.Float(compute='_earned_value',
                      string='PV',
                      digits_compute=dp.get_precision('Account'),
                      help="""Planned Value (PV) or Budgeted Cost of Work
                      Scheduled is the total cost of the work
                      scheduled/planned as of a reporting date.""")
    ev = fields.Float(compute='_earned_value',
                      string='EV',
                      digits_compute=dp.get_precision('Account'),
                      help="""Earned Value (PV) or Budgeted Cost of Work
                      Performed is the amount of work that has been
                      completed to date, expressed as the planned value for
                      that work.""")
    ac = fields.Float(compute='_earned_value',
                      string='AC',
                      digits_compute=dp.get_precision('Account'),
                      help="""Actual Cost (AC) or Actual Cost of Work
                      Performed is an indication of the level of resources
                      that have been expended to achieve the actual work
                      performed to date.""")
    cv = fields.Float(compute='_earned_value',
                      string='CV',
                      digits_compute=dp.get_precision('Account'),
                      help="""Cost Variance (CV) shows whether a project is
                      under or over budget. It is determined as EV - AC. A
                      negative value indicates that the project is over
                      budget.""")
    cvp = fields.Float(compute='_earned_value',
                       string='CVP',
                       digits_compute=dp.get_precision('Account'),
                       help="""Cost Variance % (CVP) shows whether a project
                       is under or over budget. It is determined as CV / EV.
                       A negative value indicates that the project is over
                       budget.""")
    cpi = fields.Float(compute='_earned_value',
                       string='CPI',
                       digits_compute=dp.get_precision('Account'),
                       help="""Cost Performance Index (CPI) indicates how
                       efficiently the team is using its resources. It is
                       determined as EV / AC. A value of 0.8 indicates that
                       the project has a cost efficiency that provides 0.8
                       worth of work for every unit spent to date.""")
    tcpi = fields.Float(compute='_earned_value', string='TCPI',
                        digits_compute=dp.get_precision('Account'),
                        help="""To-Complete Cost Performance Index (TCPI)
                        helps the team determine the efficiency that must be
                        achieved on the remaining work for a project to meet
                        the Budget at Completion (BAC). It is determined as
                        (BAC - EV) / (BAC - AC)""")
    sv = fields.Float(compute='_earned_value', string='SV',
                      digits_compute=dp.get_precision('Account'),
                      help="""Schedule Variance (SV) determines whether a
                      project is ahead or behind schedule. It is calculated
                      as EV - PV. A negative value indicates an unfavorable
                      condition.""")
    svp = fields.Float(compute='_earned_value', string='SVP',
                       digits_compute=dp.get_precision('Account'),
                       help="""Schedule Variance % (SVP) determines whether
                       a project is ahead or behind schedule. It is
                       calculated as SV / PV. A negative value indicates
                       what percent of the planned work has not been
                       accomplished""")
    spi = fields.Float(compute='_earned_value', string='SPI',
                       digits_compute=dp.get_precision('Account'),
                       help="""Schedule Performance Index (SPI) indicates
                       how efficiently the project team is using its time.
                       It is calculated as EV / PV. For example, on a day,
                       indicates how many hours worth of the planned work
                       is being performed.""")
    eac = fields.Float(compute='_earned_value', string='EAC',
                          digits_compute=dp.get_precision('Account'),
                          help="""Estimate at Completion (EAC) provides
                          an estimate of the final cost of the project if
                          current performance trends continue. It is
                          calculated as BAC / CPI.""")
    etc = fields.Float(compute='_earned_value', string='ETC',
                       digits_compute=dp.get_precision('Account'),
                       help="""Estimate to Complete (ETC) provides an
                       estimate of what will the remaining work cost. It is
                       calculated as (BAC - EV) / CPI.""")
    vac = fields.Float(compute='_earned_value', string='VAC',
                       digits_compute=dp.get_precision('Account'),
                       help="""Variance at Completion (VAC) shows the team
                       whether the project will finish under or over budget.
                       It is calculated as BAC - EAC.""")
    vacp = fields.Float(compute='_earned_value', string='VACP',
                        digits_compute=dp.get_precision('Account'),
                        help="""Variance at Completion % (VACP) shows the
                        team whether the project will finish under or over
                        budget. It is calculated as VAC / BAC.""")
    bac = fields.Float(compute='_earned_value', string='BAC',
                       digits_compute=dp.get_precision('Account'),
                       help="Budget at Completion (BAC)")
    pcc = fields.Float(compute='_earned_value', string='PCC',
                       digits_compute=dp.get_precision('Account'),
                       help="Costs to date / Total costs")
    poc = fields.Float(compute='_earned_value', string='POC',
                       digits_compute=dp.get_precision('Account'),
                       help="Aggregated Percent of Completion")

    def update_project_evm(self):

        project_task_obj = self.env['project.task']
        project_evm_obj = self.env['project.evm.task']
        employee_obj = self.env['hr.employee']
        cr = self.env.cr
        project = self

        # Delete current project.evm records
        project_evm_obj.search([('project_id', '=', project.id)]).unlink()

        # Get earliest and latest dates
        datetime_start, datetime_end = self._get_earliest_latest_dates()

        # Read the non-cancelled tasks associated to the project
        project_tasks = project_task_obj.search(
            [('project_id', '=', project.id)])

        # Fetch the cost of the employees assigned to these tasks
        user_cost = {}
        for project_task in project_tasks:
            user_id = project_task.user_id.id or False
            if user_id:
                user_cost[user_id] = employee_obj.get_employee_cost(user_id)

        datetime_start -= timedelta(days=5)
        datetime_end += timedelta(days=5)
        l_days = list(rrule(DAILY, dtstart=datetime_start,
                            until=datetime_end))

        # Planned value
        pv = 0.0
        # Earned Value
        ev = 0.0
        # Actual cost
        ac = 0.0

        # Budget at Completion
        bac = self._get_budget_at_completion()

        records = []
        for day_datetime in l_days:
            day_date = day_datetime.date()
            # Actual work completed today for tasks in this project
            time_start = datetime.strptime('00:00:00', '%H:%M:%S').time()
            time_end = datetime.strptime('23:59:59', '%H:%M:%S').time()

            datetime_start = datetime.combine(day_date,time_start)
            datetime_end = datetime.combine(day_date,time_end)

            cr.execute('''SELECT PTW.user_id, sum(PTW.hours)
                       FROM project_task_work AS PTW
                       LEFT JOIN project_task as PT
                       ON (PTW.task_id=PT.id)
                       WHERE PT.project_id=%s
                       AND PTW.date BETWEEN %s AND %s
                       GROUP BY PTW.user_id''',
                       (project.id, datetime_start,
                        datetime_end))
            for user_id, hours_worked in cr.fetchall():
                employee_cost = employee_obj.get_employee_cost(user_id)
                ac += employee_cost * hours_worked

            for project_task in project_tasks:
                # Record earned value according to % completed
                datetime_stage = datetime.strptime(
                    project_task.date_last_stage_update,
                    "%Y-%m-%d %H:%M:%S")
                date_done = datetime_stage.date()
                if date_done == day_date:
                    ev += user_cost.get(project_task.user_id.id, 0.0) * \
                          project_task.planned_hours * \
                          project_task.stage_id.poc / 100

                # If task is planned to complete on this date then
                # record planned value
                if project_task.date_end:
                    task_end_dt = datetime.strptime(
                        project_task.date_end, "%Y-%m-%d %H:%M:%S")
                    date_end = task_end_dt.date()
                else:
                    date_end = False

                if date_end == day_date:
                    pv += user_cost.get(project_task.user_id.id, 0.0) * \
                          project_task.planned_hours

            ratios = self._get_evm_ratios(ac, pv, ev, bac)
            # Create the EVM records
            records.extend(project.create_evm_record(day_date, ratios))
        return records

    def create_evm_record(self, eval_date, ratios):
        records = []
        project_evm_obj = self.env['project.evm.task']
        for kpi_type in ratios.keys():
            vals_lines = {'name': '',
                          'date': eval_date,
                          'eval_date': eval_date,
                          'kpi_type': kpi_type.upper(),
                          'project_id': self.id,
                          'kpi_value': ratios[kpi_type],
                          }
            records.extend([project_evm_obj.create(vals_lines).id])
        return records
