# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.project.controllers.portal import ProjectCustomerPortal


class ProjectSharePortal(ProjectCustomerPortal):
    def _prepare_project_sharing_session_info(self, project, task=None):
        res = super()._prepare_project_sharing_session_info(project, task=task)
        res["user_context"]["draggable"] = bool(
            project._check_project_sharing_access(check_readonly=True)
        )
        return res
