# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class Project(models.Model):
    _inherit = "project.project"

    internal_collaborator_ids = fields.Many2many(
        string="Collaborators",
        comodel_name="res.users",
        relation="project_user_colabor_rel",
        column1="project_id",
        column2="user_id",
        compute="_compute_collaborator_ids",
        store=True,
        readonly=False,
    )

    access_collaborators = fields.Boolean(
        default=False,
        help="Allows to access the collaborators of the project",
        compute="_compute_access_collaborators",
    )

    def _compute_access_collaborators(self):
        """
        This method checks if the current user has
        'project.group_project_user' or
        'project.group_project_manager'. If it has one
        of the group, it sets the value to True otherwise False
        """
        for project in self:
            project.access_collaborators = self.env.user.user_has_groups(
                "project.group_project_user, project.group_project_manager"
            )

    @api.depends("task_ids.user_ids", "task_ids.activity_ids")
    def _compute_collaborator_ids(self):
        """
        This method depends on the changes in the user_ids and
        activity_ids of the project's task.

        If the configuration parameters are not set, the method
        returns without computing collaborator IDs.
        It retrieves the follower IDs from the message followers
        of the project and searches for users based on task and
        activity assignments.
        Then it filters out the users who are already followers
        and assigns the remaining users as collaborator IDs for
        the project.

        :return: None
        """
        (
            collaborators_task_assigned,
            collaborators_activity_assigned,
        ) = self.get_collaborator_config_parameters()
        if not any((collaborators_task_assigned, collaborators_activity_assigned)):
            return
        collaborator_ids = self.env["res.users"]
        follower_ids = collaborator_ids.search(
            [("partner_id", "in", self.mapped("message_follower_ids.partner_id").ids)]
        )
        for record in self:
            if collaborators_task_assigned:
                collaborator_ids |= record.task_ids.mapped("user_ids")
            if collaborators_activity_assigned:
                collaborator_ids |= record.task_ids.mapped("activity_ids.user_id")
            record.internal_collaborator_ids = collaborator_ids.filtered(
                lambda user: user.id not in follower_ids.ids
            )

    @api.model
    def get_collaborator_config_parameters(self):
        """Get the configuration parameters for collaborators
        task and activity assigned."""
        ICP = self.env["ir.config_parameter"].sudo()
        collaborators_task_assigned = ICP.get_param(
            "project_collaborator.collaborators_task_assigned",
            False,
        )
        collaborators_activity_assigned = ICP.get_param(
            "project_collaborator.collaborators_activity_assigned",
            False,
        )
        return (collaborators_task_assigned, collaborators_activity_assigned)
