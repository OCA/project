# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright :
#        (c) 2014 Antiun Ingenieria, SL (Madrid, Spain, http://www.antiun.com)
#                 Endika Iglesias <endikaig@antiun.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, _
from openerp.exceptions import Warning
from datetime import timedelta
import pytz


class ProjectTask(models.Model):
    _inherit = 'project.task'

    from_days = fields.Integer(
        string='From days',
        help='Anticipation days from date begin or date end', default=0)
    estimated_days = fields.Integer(
        string='Estimated days', help='Estimated days to end', default=1)

    @api.one
    @api.constrains('estimated_days')
    def _estimated_days_check(self):
        if not self.estimated_days > 0:
            raise Warning(_('Estimated days must be greater than 0.'))

    def _count_days_without_weekend(self, date_start, date_end):
        days = (date_end - date_start).days
        return sum(1 for x in xrange(days)
                   if (date_start + timedelta(x)).weekday() < 5)

    def _count_days_weekend(self, date_start, date_end):
        days = (date_end - date_start).days
        return sum(1 for x in xrange(days)
                   if (date_start + timedelta(x)).weekday() >= 5)

    def _correct_days_to_workable(self, date, increment=True):
        while date.weekday() >= 5:
            if increment:
                date += timedelta(days=1)
            else:
                date -= timedelta(days=1)
        return date

    def _calculate_date_without_weekend(self, date_start, days,
                                        increment=True):
        total_days = 0
        c = 0
        if days < 0:
            if increment:
                increment = False
            else:
                increment = True
        days = days if days >= 0 else days * -1
        first = True
        while days != total_days:
            if total_days > 0 or not first:
                recalculate = days + (days - total_days) + c
                c += 1
            else:
                first = False
                recalculate = days
            if increment:
                start = date_start
                end = date_start + timedelta(days=recalculate)
            else:
                start = date_start - timedelta(days=recalculate)
                end = date_start
            total_days = self._count_days_without_weekend(start, end)
        if total_days > 0:
            date = end if increment else start
        else:
            date = date_start
        return self._correct_days_to_workable(date, increment)

    def on_change_dates(self, date_start, date_end, vals):
        if not date_start or not date_end:
            return vals
        start = fields.Date.from_string(date_start)
        end = fields.Date.from_string(date_end)
        end += timedelta(1)
        vals['estimated_days'] = self._count_days_without_weekend(start, end)
        calculation_type = self.project_id.calculation_type
        if calculation_type:
            if calculation_type == 'date_begin':
                if not self.project_id.date_start:
                    return vals
                aux_start = fields.Date.from_string(self.project_id.date_start)
                aux_end = start
            else:
                if not self.project_id.date:
                    return vals
                aux_start = start
                aux_end = fields.Date.from_string(self.project_id.date)
            vals['from_days'] = self._count_days_without_weekend(
                aux_start, aux_end)
        return vals

    @api.multi
    def write(self, vals):
        if (not self.env.context.get('project_recalculate')
                and (vals.get('date_start') or vals.get('date_end'))):
            date_start = (vals.get('date_start')
                          if vals.get('date_start') else self.date_start)
            date_end = (vals.get('date_end')
                        if vals.get('date_end') else self.date_end)
            vals = self.on_change_dates(date_start, date_end, vals)
        if 'estimated_days' in vals and vals['estimated_days'] < 1:
            vals['estimated_days'] = 1
        return super(ProjectTask, self).write(vals)

    def _tz_date_recalculate(self, date):
        tz = self.env.user.tz
        date = fields.Datetime.from_string(date)
        local = pytz.timezone(tz)
        seconds_to_utc = local.utcoffset(date).seconds
        date -= timedelta(seconds=seconds_to_utc)
        return fields.Datetime.to_string(date)

    def _apply_company_workday(self, date, start=True):
        date = fields.Datetime.from_string(date)
        company = self.env.user.company_id
        hour = company.workday_begin if start else company.workday_end
        seconds = hour * 3600
        date += timedelta(seconds=seconds)
        return fields.Datetime.to_string(date)

    def task_recalculate(self):
        self.ensure_one()
        increment = self.project_id.calculation_type == 'date_begin'
        if increment:
            if not self.project_id.date_start:
                raise Warning(_('Start Date field must be defined.'))
            project_date = fields.Datetime.from_string(
                self.project_id.date_start)
        else:
            if not self.project_id.date:
                raise Warning(_('End Date field must be defined.'))
            project_date = fields.Datetime.from_string(self.project_id.date)
        date_start = self._calculate_date_without_weekend(
            project_date, self.from_days, increment=increment)
        task_date_start = fields.Datetime.to_string(date_start)
        task_date_end = fields.Datetime.to_string(
            self._calculate_date_without_weekend(
                date_start, self.estimated_days - 1))
        task_date_start = self._tz_date_recalculate(task_date_start)
        task_date_end = self._tz_date_recalculate(task_date_end)
        task_date_start = self._apply_company_workday(task_date_start)
        task_date_end = self._apply_company_workday(task_date_end, False)
        self.write({'date_start': task_date_start, 'date_end': task_date_end})
