# -*- coding: utf-8 -*-
# © 2014 Daniel Reis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class ProjectTask(models.Model):

    _name = 'project.task'
    _inherit = ['project.task', 'project.sla.controlled']
