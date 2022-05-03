from odoo import models


class ProjectProject(models.Model):
    _name = "project.project"
    _inherit = ["project.project", "mail.activity.mixin"]
