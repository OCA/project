# -*- coding: utf-8 -*-
# Copyright 2016 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import date, timedelta

from openerp import api, fields, models


class ProjectTaskAlert(models.Model):
    _description = 'Task Alerts'
    _name = 'project.task.alert'

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
    last_run = fields.Date(default=fields.Date.today())
    user_id = fields.Many2one("res.users", string="Assigned to")
    task_description = fields.Char(
        help="The use of placeholders is allowed format like %(fieldname)s "
             "is used. Example: %(name)s %(description)s"
    )
    active = fields.Boolean(default=True)

    @classmethod
    def _merge_placeholders(cls, incoming, rec):
        values = rec.read()
        result = (values and incoming % values) or incoming
        return result

    @api.multi
    def _create_task_alerts(self):

        def get_user_id(user):
            user_id = user and user.id or None
            return user_id

        self.ensure_one()

        days_delta = timedelta(days=self.days_delta)
        to_date = str(date.today() + days_delta)
        last_run = self.last_run or fields.Date.today()
        task_alert_date = self.date_field_id.name
        args = [
            (task_alert_date, '!=', False),
            (task_alert_date, '<=', to_date),
            (task_alert_date, '>=', last_run),
        ]
        model_name = self.date_field_id.model_id.model
        resources = self.env[model_name].search(args)
        for resource in resources:
            # Check if the task has already been created
            if self.check_task_created(resource, to_date):
                continue

            name = self._merge_placeholders(self.name, resource)
            description = ''
            if self.task_description:
                description = self._merge_placeholders(
                    self.task_description, resource)
            user_id = get_user_id(self.user_id)
            task_data = {
                'name': name,
                'project_id': self.project_id.id,
                'user_id': user_id,
                'description': description,
                'alert_model_name': resource._name,
                'alert_res_id': resource.id,
                'alert_field_name': self.date_field_id.name,
                'alert_to_date': to_date,
                'alert_origin_id': self.id,
            }
            self.env['project.task'].create(task_data)
        self.last_run = fields.Date.today()

    @api.multi
    def create_task_alerts(self):
        for task_alert in self:
            task_alert._create_task_alerts()

    @api.multi
    def check_task_created(self, resource, to_date):
        self.ensure_one()
        ref_date = resource[self.date_field_id.name]
        prev_tasks = self.env['project.task'].search([
            ('alert_res_id', '=', resource.id),
            ('alert_model_name', '=', resource._name),
            ('alert_field_name', '=', self.date_field_id.name),
            ('alert_to_date', '<=', to_date),
        ])
        is_already_created = False
        for prev_task in prev_tasks:
            prev_to_date = prev_task.alert_to_date
            if prev_to_date >= to_date or ref_date <= prev_to_date:
                is_already_created = True
                break
        return is_already_created

    @api.model
    def run_task_alerts(self):
        alert_ids = self.search([])
        alert_ids.create_task_alerts()
