# -*- coding: utf-8 -*-
# © 2016 ONESTEiN BV (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta
from openerp import models, fields, api
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DF


class ProjectTaskAlert(models.Model):
    _description = 'Task Alerts'
    _name = 'project.task.alert'
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
        'ir.model.fields',
        string="Date field",
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

    @api.model
    def _merge_placeholders(self, incoming, rec):
        values = rec.read()
        try:
            result = incoming % values
        except:
            result = incoming
        return result

    @api.multi
    def create_task_alerts(self):
        for task_alert in self:
            days_delta = timedelta(days=task_alert.days_delta)
            to_date = (datetime.now() + days_delta).strftime(DF)
            args = [
                (task_alert.date_field_id.name, '<=', to_date),
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
            rec_ids = self.env[model_name].search(args)
            for rec in rec_ids:
                # Check if the task has already been created
                if self.env['project.task'].search([
                    ('alert_res_id', '=', rec.id),
                    ('alert_model_name', '=', rec._name),
                    ('alert_field_name', '=', task_alert.date_field_id.name)
                ]):
                    continue
                task_name = self._merge_placeholders(
                    task_alert.task_name, rec)
                description = ''
                if task_alert.task_description:
                    description = self._merge_placeholders(
                        task_alert.task_description, rec)
                userid = task_alert.user_id and task_alert.user_id.id or None
                task_data = {
                    'name': task_name,
                    'project_id': task_alert.project_id.id,
                    'user_id': userid,
                    'description': description,
                    'alert_model_name': rec._name,
                    'alert_res_id': rec.id,
                    'alert_field_name': task_alert.date_field_id.name,
                }
                self.env['project.task'].create(task_data)
            task_alert.last_run = datetime.now()

    @api.model
    def run_task_alerts(self):
        alert_ids = self.search([])
        alert_ids.create_task_alerts()
