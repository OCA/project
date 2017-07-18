# -*- coding: utf-8 -*-
# © 2016 ONESTEiN BV (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DF


class TaskAlert(models.Model):
    _description = 'Task Alerts'
    _name = 'task.alert'
    _rec_name = 'task_name'

    active = fields.Boolean(string='Active', default=True)
    project_id = fields.Many2one(
        'project.project',
        string="Project",
        required=True
    )
    days_delta = fields.Integer(
        string="Interval in days",
        help="The amount of days before the date in the "
             "field to send out the alert.",
        required=True
    )
    date_field_id = fields.Many2one(
        'ir.model.fields', string="Date field",
        domain=[('ttype', 'in', ('date', 'datetime'))],
        required=True
    )
    task_name = fields.Char(
        string="Task Name",
        required=True,
        help="The use of placeholders is allowed format "
             "like %(fieldname)s is used. Example: %(name)s %(description)s"
    )
    last_run = fields.Datetime("Last run", default=datetime.now())
    user_id = fields.Many2one("res.users", string="Assigned to")
    task_description = fields.Char(
        string="Task Description",
        help="The use of placeholders is allowed format like %(fieldname)s "
             "is used. Example: %(name)s %(description)s"
    )

    def _create_task(self, task_data):
        res = []
        if task_data:
            task = self.env['project.task']
            res = task.create(task_data)
        return res

    @api.cr_uid_context
    def _merge_placeholders(self, cr, uid, incoming, rec, context=None):
        obj = self.pool.get(rec._name)
        values = obj.read(cr, uid, rec.id, [], context=context)
        try:
            result = incoming % values
        except:
            result = incoming
        return result

    def run(self, cr, uid, ids, context=None):

        # TODO check if we should allow setting task_alert to inactive
        alert_ids = self.search(cr, uid, [], context=context)
        for task_alert in self.browse(cr, uid, alert_ids, context=context):
            days_delta = timedelta(days=task_alert.days_delta)
            to_date = (datetime.now() + days_delta).strftime(DF)
            args = [(task_alert.date_field_id.name, '<=', to_date),
                    (task_alert.date_field_id.name, '!=', False)
                    ]
            if not task_alert.last_run:
                task_alert.last_run = datetime.now()
            last_run_dt = datetime.strptime(task_alert.last_run, DF)
            last_run = (last_run_dt).strftime(DF)
            args.append(
                (task_alert.date_field_id.name, '>=', last_run)
            )
            model_name = task_alert.date_field_id.model_id.model
            model_obj = self.pool.get(model_name)
            rec_ids = model_obj.search(cr, uid, args, context=context)
            for rec in model_obj.browse(cr, uid, rec_ids, context=context):
                # Check if the task has already been created
                if self.pool.get('project.task').search(cr, uid, [
                    ('alert_res_id', '=', rec.id),
                    ('alert_model_name', '=', rec._name),
                    ('alert_field_name', '=', task_alert.date_field_id.name)
                ], context=context):
                    continue
                task_name = task_alert.task_name
                task_description = task_alert.task_description
                description = task_description and self._merge_placeholders(
                    cr, uid, task_description, rec, context=context
                ) or ''
                task_data = {
                    'name': self._merge_placeholders(
                        cr, uid, task_name, rec, context=context),
                    'project_id': task_alert.project_id.id,
                    'user_id': task_alert.user_id.id,
                    'description': description,
                    'alert_model_name': rec._name,
                    'alert_res_id': rec.id,
                    'alert_field_name': task_alert.date_field_id.name,
                }
                task_alert._create_task(task_data)
            task_alert.last_run = datetime.now()
        return True
