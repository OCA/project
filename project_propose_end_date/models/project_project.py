# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class Project(models.Model):
    _inherit = "project.project"

    @api.multi
    @api.onchange('date_start')
    def onchange_date_start(self):
        for project in self:
            if project.date_start and not project.date:
                project.date = project.date_start
