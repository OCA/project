# -*- coding: utf-8 -*-

from odoo import models, api, _
from odoo.exceptions import UserError


class ProjectProject(models.Model):
    _inherit = 'project.project'

    @api.multi
    def project_recalculate(self):
        """
            Recalculate project tasks start and end dates.
            After that, recalculate new project start or end date
        """
        for project in self:
            if not project.calculation_type:
                raise UserError(_("Cannot recalculate project because your "
                                  "project doesn't have calculation type."))
            if (project.calculation_type == 'date_begin' and not
                    project.date_start):
                raise UserError(_("Cannot recalculate project because your "
                                  "project doesn't have date start."))
            if (project.calculation_type == 'date_end' and not
                    project.date):
                raise UserError(_("Cannot recalculate project because your "
                                  "project doesn't have date end."))
            project.tasks.task_recalculate(project.calculation_type)
            vals = project._start_end_dates_prepare()
            if vals:
                project.write(vals)
        return True
