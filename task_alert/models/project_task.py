# -*- coding: utf-8 -*-
# © 2016 ONESTEiN BV (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class ProjectTask(models.Model):
    _inherit = 'project.task'

    alert_model_name = fields.Char('Alert Model Name')
    alert_res_id = fields.Integer('Alert Resource ID')
    alert_field_name = fields.Char('Alert Date Field Name')
