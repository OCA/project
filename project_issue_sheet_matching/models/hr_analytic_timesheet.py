# -*- coding: utf-8 -*-
# © 2017 Sunflower IT (http://sunflowerweb.nl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openerp import models

_logger = logging.getLogger(__name__)


class HrAnalyticTimesheet(models.Model):
    _name = 'hr.analytic.timesheet'
    _inherit = ['hr.analytic.timesheet', 'ir.needaction_mixin']

    def _needaction_domain_get(self, cr, uid, context=None):
        if self._needaction:
            return [('issue_id', '=', False)]
        return []
