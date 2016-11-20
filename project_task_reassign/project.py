# -*- coding: utf-8 -*-
# Copyright 2013 Daniel Reis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api, _


class ProjectIssue(models.Model):
    _inherit = 'project.task'

    @api.multi
    def do_reassign(self, user=None, proj=None):
        """ Reassign an Task to another User and/or Project """
        assert user or proj, _("No reassignment data was provided.")
        # write reassignment changes
        reassign_data = {}
        if user:
            reassign_data['user_id'] = user
        if proj:
            reassign_data['project_id'] = proj
        return self.write(reassign_data)
