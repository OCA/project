# -*- coding: utf-8 -*-
# © 2016 ONESTEiN BV (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import date, timedelta
from openerp import models, fields, api


class ProjectTaskAlert(models.Model):
    _description = 'Task Alerts'
    _name = 'project.task.alert'

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
    name = fields.Char(
        string="Task Name",
        required=True,
        help="The use of placeholders is allowed format "
             "like %(fieldname)s is used. Example: %(name)s %(description)s"
    )
    last_run = fields.Date("Last run", default=fields.Date.today())
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
            to_date = str(date.today() + days_delta)
            last_run = task_alert.last_run or fields.Date.today()
            task_alert_date = task_alert.date_field_id.name
            args = [
                (task_alert_date, '!=', False),
                (task_alert_date, '<=', to_date),
                (task_alert_date, '>=', last_run),
            ]
            model_name = task_alert.date_field_id.model_id.model
            rec_ids = self.env[model_name].search(args)
            for rec in rec_ids:
                # Check if the task has already been created
                ref_date = rec[task_alert.date_field_id.name]
                prev_tasks = self.env['project.task'].search([
                    ('alert_res_id', '=', rec.id),
                    ('alert_model_name', '=', rec._name),
                    ('alert_field_name', '=', task_alert.date_field_id.name),
                    ('alert_to_date', '<=', to_date),
                ])
                to_continue = False
                for prev_task in prev_tasks:
                    prev_to_date = prev_task.alert_to_date
                    if prev_to_date >= to_date:
                        to_continue = True
                        break
                    elif ref_date <= prev_to_date:
                        to_continue = True
                        break
                if to_continue:
                    continue

                name = self._merge_placeholders(
                    task_alert.name, rec)
                description = ''
                if task_alert.task_description:
                    description = self._merge_placeholders(
                        task_alert.task_description, rec)
                userid = task_alert.user_id and task_alert.user_id.id or None
                task_data = {
                    'name': name,
                    'project_id': task_alert.project_id.id,
                    'user_id': userid,
                    'description': description,
                    'alert_model_name': rec._name,
                    'alert_res_id': rec.id,
                    'alert_field_name': task_alert.date_field_id.name,
                    'alert_to_date': to_date,
                    'alert_origin_id': task_alert.id,
                }
                self.env['project.task'].create(task_data)
            task_alert.last_run = fields.Date.today()

    @api.model
    def run_task_alerts(self):
        alert_ids = self.search([])
        alert_ids.create_task_alerts()
