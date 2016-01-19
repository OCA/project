# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, models


class BusinessRequirement(models.Model):
    _inherit = "business.requirement"

    @api.multi
    def generate_projects_wizard(self):
        res = self.project_id.with_context(
            br_ids=self).generate_projects_wizard()
        return res
