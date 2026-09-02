# Copyright (C) 2025 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.project.controllers.portal import ProjectCustomerPortal


class ProjectCustomerPortalInherit(ProjectCustomerPortal):
    def _task_get_page_view_values(self, task, access_token, **kwargs):
        """Override to return portal description if enabled."""
        values = super()._task_get_page_view_values(task, access_token, **kwargs)
        if task.use_portal_description:
            values["description"] = task.portal_description
        return values
