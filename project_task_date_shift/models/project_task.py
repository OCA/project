from odoo import models, fields


class ProjectTask(models.Model):
    _inherit = 'project.task'
    _order = 'priority desc, date_start, date_end, sequence, id desc'

    date_start = fields.Datetime(string='Starting Date',
                                 default=fields.Datetime.now,
                                 index=True,
                                 copy=True)
