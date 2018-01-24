# -*- coding: utf-8 -*-
# © 2013 Daniel Reis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class ProjectIssue(models.Model):
    """
    Extend Project Issues to be SLA Controlled
    """
    _name = 'project.issue'
    _inherit = ['project.issue', 'project.sla.controlled']
