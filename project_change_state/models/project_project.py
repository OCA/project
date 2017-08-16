# -*- coding: utf-8 -*-
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# © 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.html).

from openerp import api, models


class ProjectProject(models.Model):
    _inherit = 'project.project'

    @api.multi
    def set_done(self):
        for rec in self:
            rec.state = 'close'

    @api.multi
    def set_cancel(self):
        for rec in self:
            rec.state = 'cancelled'

    @api.multi
    def set_pending(self):
        for rec in self:
            rec.state = 'pending'

    @api.multi
    def set_open(self):
        for rec in self:
            rec.state = 'open'
