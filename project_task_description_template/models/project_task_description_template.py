# Copyright 2023 - Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo import fields, models


class ProjectTaskDescriptionTemplate(models.Model):
    _name = "project.task.description.template"
    _description = "Project Task Description Template"

    name = fields.Char(required=True)
    description = fields.Html(required=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)
    project_ids = fields.Many2many(
        "project.project",
        "project_task_description_template_project_rel",
        "template_id",
        "project_id",
        string="Projects",
        help="Leave empty to make the template available in all projects. "
        "Portal users only see the templates linked to their projects.",
    )

    def write(self, vals):
        projects = self.project_ids
        res = super().write(vals)
        if "project_ids" in vals or "active" in vals:
            projects._check_portal_task_description_template_required()
        return res

    def unlink(self):
        projects = self.project_ids
        res = super().unlink()
        projects._check_portal_task_description_template_required()
        return res
