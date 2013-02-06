# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012 Daniel Reis
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

from openerp.osv import fields, orm
from datetime import datetime


class project_issue(orm.Model):
    _inherit = 'project.issue'

    # `_compute_day` backported from v7.0 (just copied actually)
    # Allows the Issue's `project_id` to be optional.
    #---- START ----
    def _compute_day(self, cr, uid, ids, fields, args, context=None):
        """
        @param cr: the current row, from the database cursor,
        @param uid: the current userâ€™s ID for security checks,
        @param ids: List of Opendayâ€™s IDs
        @return: difference between current date and log date
        @param context: A standard dictionary for contextual values
        """
        cal_obj = self.pool.get('resource.calendar')
        res_obj = self.pool.get('resource.resource')

        res = {}
        for issue in self.browse(cr, uid, ids, context=context):
            res[issue.id] = {}
            for field in fields:
                duration = 0
                ans = False
                hours = 0

                date_create = datetime.strptime(issue.create_date, "%Y-%m-%d %H:%M:%S")
                if field in ['working_hours_open','day_open']:
                    if issue.date_open:
                        date_open = datetime.strptime(issue.date_open, "%Y-%m-%d %H:%M:%S")
                        ans = date_open - date_create
                        date_until = issue.date_open
                        #Calculating no. of working hours to open the issue
                        if issue.project_id.resource_calendar_id:
                            hours = cal_obj.interval_hours_get(cr, uid, issue.project_id.resource_calendar_id.id,
                                                           date_create,
                                                           date_open)
                elif field in ['working_hours_close','day_close']:
                    if issue.date_closed:
                        date_close = datetime.strptime(issue.date_closed, "%Y-%m-%d %H:%M:%S")
                        date_until = issue.date_closed
                        ans = date_close - date_create
                        #Calculating no. of working hours to close the issue
                        if issue.project_id.resource_calendar_id:
                            hours = cal_obj.interval_hours_get(cr, uid, issue.project_id.resource_calendar_id.id,
                               date_create,
                               date_close)
                elif field in ['days_since_creation']:
                    if issue.create_date:
                        days_since_creation = datetime.today() - datetime.strptime(issue.create_date, "%Y-%m-%d %H:%M:%S")
                        res[issue.id][field] = days_since_creation.days
                    continue

                elif field in ['inactivity_days']:
                    res[issue.id][field] = 0
                    if issue.date_action_last:
                        inactive_days = datetime.today() - datetime.strptime(issue.date_action_last, '%Y-%m-%d %H:%M:%S')
                        res[issue.id][field] = inactive_days.days
                    continue
                if ans:
                    resource_id = False
                    if issue.user_id:
                        resource_ids = res_obj.search(cr, uid, [('user_id','=',issue.user_id.id)])
                        if resource_ids and len(resource_ids):
                            resource_id = resource_ids[0]
                    duration = float(ans.days)
                    if issue.project_id and issue.project_id.resource_calendar_id:
                        duration = float(ans.days) * 24

                        new_dates = cal_obj.interval_min_get(cr, uid,
                                                             issue.project_id.resource_calendar_id.id,
                                                             date_create,
                                                             duration, resource=resource_id)
                        no_days = []
                        date_until = datetime.strptime(date_until, '%Y-%m-%d %H:%M:%S')
                        for in_time, out_time in new_dates:
                            if in_time.date not in no_days:
                                no_days.append(in_time.date)
                            if out_time > date_until:
                                break
                        duration = len(no_days)

                if field in ['working_hours_open', 'working_hours_close']:
                    res[issue.id][field] = hours
                else:
                    res[issue.id][field] = abs(float(duration))

        return res
    #---- END ----

    _columns = {
        'regarding_uid': fields.many2one('res.users', 'Regarding User',
            help="User affected by the Issue"),
            
        # `_compute_day` backport: redeclaring columns in order to 
        # rebuild references for the replaced method
        #---- START ----
        'days_since_creation': fields.function(_compute_day, string='Days since creation date', \
                                               multi='compute_day', type="integer", help="Difference in days between creation date and current date"),
        'day_open': fields.function(_compute_day, string='Days to Open', \
                                multi='compute_day', type="float", store=True),
        'day_close': fields.function(_compute_day, string='Days to Close', \
                                multi='compute_day', type="float", store=True),
        'working_hours_open': fields.function(_compute_day, string='Working Hours to Open the Issue', \
                                multi='compute_day', type="float", store=True),
        'working_hours_close': fields.function(_compute_day, string='Working Hours to Close the Issue', \
                                multi='compute_day', type="float", store=True),
        'inactivity_days': fields.function(_compute_day, string='Days since last action', \
                                multi='compute_day', type="integer", help="Difference in days between last action and current date"),
        #---- END ----
    }
    _defaults = {
        'regarding_uid': lambda s, cr, uid, c: uid,
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
