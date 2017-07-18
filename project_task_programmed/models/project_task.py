# -*- coding: utf-8 -*-
# Copyright 2016 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    alert_model_name = fields.Char()
    alert_res_id = fields.Integer('Alert Resource ID')
    alert_field_name = fields.Char('Alert Date Field Name')
    alert_to_date = fields.Date('Alert Date Limit')
    alert_origin_id = fields.Many2one(
        'project.task.alert',
        string='Created by Alert')
