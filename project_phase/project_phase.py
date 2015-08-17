
##############################################################################
#
#    Copyright (C) 2006 - 2015 BHC SPRL www.bhc.be
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
from datetime import datetime
from openerp.tools.translate import _
from openerp.osv import fields, osv
from openerp.addons.resource.faces import task as Task

class project_phase(osv.osv):
    _name = "project.phase"
    _description = "Project Phase"
    _inherit = ['mail.thread']
    _track = {
        'state': {
            'project_phase.mt_phase_change': lambda self, cr, uid, obj, ctx=None: True 
        },
    }
    def _check_dates(self, cr, uid, ids, context=None):
         for phase in self.read(cr, uid, ids, ['date_start', 'date_end'], context=context):
             if phase['date_start'] and phase['date_end'] and phase['date_start'] > phase['date_end']:
                 return False
         return True

    def _compute_progress(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        if not ids:
            return res
        for phase in self.browse(cr, uid, ids, context=context):
            if phase.state=='done':
                res[phase.id] = 100.0
                continue
            elif phase.state=="cancelled":
                res[phase.id] = 0.0
                continue
            elif not phase.task_ids:
                res[phase.id] = 0.0
                continue
            tot = done = 0.0
            for task in phase.task_ids:
                tot += task.total_hours
                done += min(task.effective_hours, task.total_hours)
            if not tot:
                res[phase.id] = 0.0
            else:
                res[phase.id] = round(100.0 * done / tot, 2)
        return res

    def _get_uom(self, cr, uid, ids, context):
        if uid:
            print uid
            res=self.pool.get('res.users').browse(cr,uid,uid).company_id.project_time_mode_id.id
        return res

    _columns = {
        'name': fields.char("Name", size=64, required=True),
        'date_start': fields.datetime('Start Date', select=True, help="It's computed by the scheduler according the project date or the end date of the previous phase.", states={'done':[('readonly',True)], 'cancelled':[('readonly',True)]}),
        'date_end': fields.datetime('End Date', help=" It's computed by the scheduler according to the start date and the duration.", states={'done':[('readonly',True)], 'cancelled':[('readonly',True)]}),
        'project_id': fields.many2one('project.project', 'Project', required=True, select=True),
        'sequence': fields.integer('Sequence', select=True, help="Gives the sequence order when displaying a list of phases."),
        'duration': fields.float('Duration', required=True, help="By default in days", states={'done':[('readonly',True)], 'cancelled':[('readonly',True)]}),
        'product_uom': fields.many2one('product.uom', 'Duration Unit of Measure', required=True, readonly=True,help="Unit of Measure (Unit of Measure) is the unit of measurement for Duration", states={'done':[('readonly',True)], 'cancelled':[('readonly',True)]}),
        'task_ids': fields.one2many('project.task', 'phase_id', "Project Tasks", states={'done':[('readonly',True)], 'cancelled':[('readonly',True)]}),
        'state': fields.selection([('draft', 'New'), ('cancelled', 'Cancelled'),('open', 'In Progress'), ('pending', 'Pending'), ('done', 'Done')], 'Status', readonly=True, required=True, track_visibility='onchange',
                                  help='If the phase is created the status \'Draft\'.\n If the phase is started, the status becomes \'In Progress\'.\n If review is needed the phase is in \'Pending\' status.\
                                  \n If the phase is over, the status is set to \'Done\'.'),
        'progress': fields.function(_compute_progress, string='Progress', help="Computed based on related tasks"),
        
     }
    
    _defaults = {
        'state': 'draft',
        'sequence': 10,
        'product_uom': lambda s, cr, uid, c: s.pool.get('project.phase')._get_uom(cr, uid, 'project.phase', context=c),
    }
    
    _order = "project_id, date_start, sequence"
    _constraints = [
        (_check_dates, 'Phase start-date must be lower than phase end-date.', ['date_start', 'date_end']),
    ]
    
    def create(self, cr, uid, vals, context=None):
        res= super(project_phase, self).create(cr, uid, vals, context)
        for i in self.browse(cr,uid,[res]):
            for j in i.task_ids:
                if i.date_end:
                    self.pool.get('project.task').write(cr,uid,j.id,{'date_deadline':i.date_end})
                if i.date_start:
                    self.pool.get('project.task').write(cr,uid,j.id,{'date_start':i.date_start})
        return res
    
    def write(self, cr, uid, ids, vals, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        for i in self.browse(cr,uid,ids):
            for j in i.task_ids:
                if vals and 'date_start' in vals:
                    self.pool.get('project.task').write(cr,uid,j.id,{'date_start':vals.get('date_start')})
                if vals and 'date_end' in vals:
                    self.pool.get('project.task').write(cr,uid,j.id,{'date_deadline':vals.get('date_end')})
        result = super(project_phase, self).write(cr, uid, ids, vals, context=context)
        return result
    
    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        if not default.get('name', False):
            default.update(name=_('%s (copy)') % (self.browse(cr, uid, id, context=context).name))
        return super(project_phase, self).copy(cr, uid, id, default, context)

    def set_draft(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state': 'draft'})
        return True

    def set_open(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state': 'open'})
        return True

    def set_pending(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state': 'pending'})
        return True

    def set_cancel(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state': 'cancelled'})
        return True

    def set_done(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state': 'done'})
        return True

project_phase()

class account_analytic_account(osv.osv):
    _inherit = 'account.analytic.account'
    _description = 'Analytic Account'
    _columns = {
        'use_phases': fields.boolean('Phases', help="Check this field if you plan to use phase-based scheduling"),
    }

    def on_change_template(self, cr, uid, ids, template_id, context=None):
        res = super(account_analytic_account, self).on_change_template(cr, uid, ids, template_id, context=context)
        if template_id and 'value' in res:
            template = self.browse(cr, uid, template_id, context=context)
            res['value']['use_phases'] = template.use_phases
        return res

    def _trigger_project_creation(self, cr, uid, vals, context=None):
        if context is None: context = {}
        res = super(account_analytic_account, self)._trigger_project_creation(cr, uid, vals, context=context)
        return res or (vals.get('use_phases') and not 'project_creation_in_progress' in context)

account_analytic_account()

class project(osv.osv):
    _inherit = "project.project"

    def _phase_count(self, cr, uid, ids, field_name, arg, context=None):
        res = dict.fromkeys(ids, 0)
        phase_ids = self.pool.get('project.phase').search(cr, uid, [('project_id', 'in', ids)])
        for phase in self.pool.get('project.phase').browse(cr, uid, phase_ids, context):
            res[phase.project_id.id] += 1
        return res

    _columns = {
        'phase_ids': fields.one2many('project.phase', 'project_id', "Project Phases"),
        'phase_count': fields.function(_phase_count, type='integer', string="Open Phases"),
    }

project()

class project_task(osv.osv):
    _inherit = "project.task"
    _columns = {
        'phase_id': fields.many2one('project.phase', 'Project Phase', domain="[('project_id', '=', project_id)]"),
    }
project_task()