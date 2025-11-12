# Copyright 2025 Marcel Savegnago - Escodoo <https://escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request

from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.addons.project.controllers.portal import ProjectCustomerPortal


class ProjectUpdatePortal(ProjectCustomerPortal):
    def _update_get_page_view_values(self, update, access_token, **kwargs):
        """Returns values for update view in portal"""
        values = {
            "page_name": "project_update",
            "update": update,
            "project": update.project_id,
            "user": request.env.user,
        }
        return self._get_page_view_values(
            update, access_token, values, "my_project_updates_history", False, **kwargs
        )

    @http.route(
        ["/my/projects/<int:project_id>/update/<int:update_id>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_project_update(
        self, project_id=None, update_id=None, access_token=None, **kw
    ):
        """Route to view a specific project update"""
        try:
            # Check project access first
            self._document_check_access("project.project", project_id)
        except (AccessError, MissingError):
            return request.redirect("/my")

        # Check update access
        try:
            update_sudo = self._document_check_access(
                "project.update", update_id, access_token
            )
        except (AccessError, MissingError):
            return request.redirect("/my/projects/%s" % project_id)

        # Check if update belongs to project
        if update_sudo.project_id.id != project_id:
            return request.redirect("/my/projects/%s" % project_id)

        values = self._update_get_page_view_values(update_sudo, access_token, **kw)
        return request.render("project_update_portal.portal_my_project_update", values)

    @http.route(
        ["/my/projects/<int:project_id>/updates"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_project_updates(self, project_id=None, page=1, **kw):
        """Route to list all updates of a project"""
        try:
            project_sudo = self._document_check_access("project.project", project_id)
        except (AccessError, MissingError):
            return request.redirect("/my")

        # Search project updates
        Update = request.env["project.update"]
        domain = [("project_id", "=", project_id)]

        # Count total updates
        update_count = Update.search_count(domain)

        # Pagination
        pager = portal_pager(
            url="/my/projects/%s/updates" % project_id,
            url_args={},
            total=update_count,
            page=page,
            step=self._items_per_page,
        )

        # Search updates
        updates = Update.search(
            domain,
            order="date desc",
            limit=self._items_per_page,
            offset=pager["offset"],
        )

        values = {
            "page_name": "project_updates",
            "project": project_sudo,
            "updates": updates,
            "pager": pager,
        }
        return request.render("project_update_portal.portal_my_project_updates", values)
