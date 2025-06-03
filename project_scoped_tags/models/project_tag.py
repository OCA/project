from logging import getLogger

from odoo import api, fields, models

_logger = getLogger(__name__)


class ProjectTags(models.Model):
    _inherit = "project.tags"

    available_in_project_ids = fields.Many2many(
        "project.project",
        "project_tags_available_project_rel",
        "tag_id",
        "project_id",
        string="Available in Projects",
        help="If empty, the tag is global and available for all projects.",
        compute="_compute_available_in_project_ids",
        readonly=False,
        store=True,
    )

    globally_available = fields.Boolean(
        compute="_compute_globally_available",
        store=True,
    )

    @api.depends("project_ids")
    def _compute_available_in_project_ids(self):
        for tag in self:
            # When a tag is added to a project, it becomes available
            # in that project and this tasks
            tag.available_in_project_ids |= tag.project_ids

    @api.depends("available_in_project_ids")
    def _compute_globally_available(self):
        for tag in self:
            # A tag is globally available if it is not linked to any project
            tag.globally_available = not tag.available_in_project_ids

    @api.model_create_multi
    def create(self, vals_list):
        tags = self.browse()
        for vals in vals_list:

            _logger.debug("Creating tag with values: %s", vals)

            name = vals.get("name")

            existing_tag = self.search([("name", "=", name)], limit=1)
            if existing_tag:
                tags += existing_tag
            else:
                tags += super(ProjectTags, self).create([vals])
        return tags
