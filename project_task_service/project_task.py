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

from osv import fields, osv
from datetime import datetime, timedelta

class task(osv.osv):
    #FUTURE: use task recurrency, to generate maintenance plans
    #FUTURE: Apply maintenance plan templates (use Project templates?)
    _inherit = "project.task"
    _columns = {
        #modified fields:
        'functional_block_id': fields.many2one('project.functional_block', 'Component', 
            help = "Component (system, module, function) to be addressed"),
        #added fields:
        'ref': fields.char('Code', 20, help="Service Order number"),
        'report_desc': fields.text('Work description'),
        'todo_desc': fields.text('Pending issues description'),
        'reason_id': fields.many2one('project.task.cause', 'Problem Cause', \
            help='Cause for the incident that made this task necessary. Available list depends on the Task Type.'),
    }

    def do_close(self, cr, uid, ids, context=None):
        #Automatically adjust Task Start and End dates based on Work details:
        for t in  self.browse(cr, uid, ids, context=context):
            task_dts = t.date_start
            task_dte = t.date_end or t.date_start
            for w in t.work_ids:
                #Task start date should not be later than the oldest work line
                work_dts = w.date
                task_dts = min(task_dts, work_dts) or work_dts
                #Task end date should not be before the last work line
                d = datetime.strptime(w.date, '%Y-%m-%d %H:%M:%S') \
                    + timedelta(seconds=round(w.hours*3600) )
                work_dte = d.strftime('%Y-%m-%d %H:%M:%S')
                task_dte = max(task_dte, work_dte) or work_dte
            vals = {'date_start': task_dts, 'date_end': task_dte}
            self.write(cr, uid, [t.id],vals, context=context)
        return super(task, self).do_close(cr, uid, ids, context)
    
task()


class project_work(osv.osv):
    #Changed Task work default Date to Y-m-d
    _inherit = "project.task.work"
    _defaults = {
        'date': lambda *a: datetime.now().strftime('%Y-%m-%d'),
    }
project_work()


class project_task_type(osv.osv):
    _inherit = 'project.task.type'
    _columns = {
        'code': fields.char('Code', size=10),
    }
project_task_type()


class project_functional_block(osv.osv):
    _inherit = 'project.functional_block'
    _columns = {
        'code': fields.char('Code', size=10),
    }
project_functional_block()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


