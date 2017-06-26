# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp import api, models, _
from openerp.exceptions import ValidationError


class ProjectProject(models.Model):
    _inherit = "project.project"

    @api.multi
    def set_pending(self):
        for project in self:
            for child in project.project_child_complete_ids:
               child.set_pending()
        super(ProjectProject, self).set_pending()

    @api.multi
    def set_open(self):
        for project in self:
            for child in project.project_child_complete_ids:
                child.set_open()
        super(ProjectProject, self).set_open()

    @api.multi
    def set_close(self):
        for project in self:
            for child in project.project_child_complete_ids:
               child.set_close()
        super(ProjectProject, self).set_close()

    @api.multi
    def set_cancel(self):
        for project in self:
            for child in project.project_child_complete_ids:
                child.set_cancel()
        super(ProjectProject, self).set_cancel()
