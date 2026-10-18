# Copyright 2026 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import Command, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    def action_assign_to_me(self):
        self.write({"user_ids": [Command.link(self.env.user.id)]})
