# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, fields, api, _
from openerp.exceptions import Warning


class ProjectProject(models.Model):
    _inherit = 'project.project'

    calculation_type = fields.Selection(
        [('none', 'No calculation'),
         ('date_begin', 'Date begin'),
         ('date_end', 'Date end')],
        string='Calculation type', default='date_begin', required=True,
        help='How to calculate tasks with date start or date end references')

    def _dates_prepare(self):
        """
            Prepare project start or end date, looking into tasks list
            and depending on project calculation_type
            - if calculation_type == 'date_begin':
                project end date = latest date from tasks end dates
            - if calculation_type == 'date_end':
                project start date = earliest date from tasks start dates

            NOTE: Do not perform any write operations to DB
        """
        vals = {}
        self.ensure_one()
        # Here we consider all project task, the ones in a stage with
        # fold = False and the ones with fold = True
        from_string = fields.Datetime.from_string
        to_string = fields.Date.to_string
        min_date_start = False
        max_date_end = False
        for task in self.tasks:
            if not task.date_start and not task.date_end:
                continue
            date_start = from_string(task.date_start or task.date_end)
            date_end = from_string(task.date_end or task.date_start)
            if not min_date_start or min_date_start > date_start:
                min_date_start = date_start
            if not max_date_end or max_date_end < date_end:
                max_date_end = date_end
        # Assign min/max dates if available
        if self.calculation_type == 'date_begin' and max_date_end:
            vals['date'] = to_string(max_date_end)
        if self.calculation_type == 'date_end' and min_date_start:
            vals['date_start'] = to_string(min_date_start)
        return vals

    @api.multi
    def project_recalculate(self):
        """
            Recalculate project tasks start and end dates.
            After that, recalculate new project start or end date
        """
        for project in self:
            if not project.calculation_type:
                raise Warning(_("Cannot recalculate project because your "
                                "project don't have calculation type."))
            if (project.calculation_type == 'date_begin'
                    and not project.date_start):
                raise Warning(_("Cannot recalculate project because your "
                                "project don't have date start."))
            if (project.calculation_type == 'date_end'
                    and not project.date):
                raise Warning(_("Cannot recalculate project because your "
                                "project don't have date end."))
            if project.calculation_type != 'none':
                for task in project.tasks:
                    task.task_recalculate()
                vals = project._dates_prepare()
                if vals:
                    project.write(vals)
        return True
