# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    task_description_template_ids = fields.Many2many(
        "project.task.description.template",
        "project_task_description_template_project_rel",
        "project_id",
        "template_id",
        string="Task Description Templates",
        help="Templates available for the tasks of this project. Templates "
        "without projects are also available for internal users.",
    )
