from odoo import _, http
from odoo.exceptions import AccessError, MissingError
from odoo.fields import Date
from odoo.http import request

from odoo.addons.project.controllers.portal import ProjectCustomerPortal


class ProjectCustomerNewPortal(ProjectCustomerPortal):
    @property
    def mandatory_task_fields(self) -> list:
        """Mandatory task fields for portal user"""
        return ["name", "description"]

    @property
    def optional_task_fields(self) -> list:
        """Optional task fields for portal user"""
        return ["date_deadline"]

    def _validate_task_fields(self, data, task_creation=False) -> tuple:
        """Validate task values submitted from the portal form."""
        error, error_message = dict(), []

        # Validation
        for field_name in self.mandatory_task_fields:
            if not data.get(field_name):
                error[field_name] = "missing"

        # Deadline validation
        date_deadline = data.get("date_deadline")
        if date_deadline:
            date = Date.to_date(data.get("date_deadline"))
            if date and date < Date.today():
                error["date_deadline"] = "invalid"
                error_message.append("Deadline is in the past")

        return error, error_message

    def _prepare_task_values(self, data) -> dict:
        """
        Prepare task values
        :param dict data: post values
        :return: prepared task values
        """
        values = {key: data[key] for key in self.mandatory_task_fields}
        values.update(
            {
                key: data[key]
                for key in self.optional_task_fields
                if key in data and data.get(key)
            }
        )
        return values

    def _task_action_page_view_values(self, project) -> dict:
        """
        Prepare values for task action page view
        :param project: project.project
        :return: dict
        """
        values = self._prepare_portal_layout_values()
        values.update(
            {
                "project": project,
                "error": {},
                "error_message": [],
            }
        )
        return values

    @http.route(
        ["/my/projects/<int:project_id>/task/new"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_project_create_task(self, project_id=None, **post) -> http.Response:
        """
        Create a task in a project
        :param int project_id: project
        :param dict post: post values
        """
        project = request.env["project.project"].sudo().browse(project_id).exists()
        if not project:
            raise MissingError(_("Project not found!"))
        if not project.is_portal_task_creation_allowed():
            raise AccessError(_("You are not allowed to create tasks in this project."))
        values = self._task_action_page_view_values(project)
        if post and request.httprequest.method == "POST":
            error, error_message = self._validate_task_fields(post)
            if not error:
                values = self._prepare_task_values(post)
                values["project_id"] = project.id
                task = request.env["project.task"].create(values)
                return request.redirect(f"/my/projects/{project_id}/task/{task.id}")
            values.update({"error": error, "error_message": error_message, **post})
        values.update({"page_name": "task_creation", "button": _("Create")})
        return request.render(
            "project_task_create_portal.portal_project_task_new", values
        )

    @http.route(
        ["/my/projects/<int:project_id>/task/<int:task_id>/edit"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_project_edit_task(self, project_id=None, task_id=None, **post):
        """
        Edit a task in a project
        :param int project_id: project.project record id
        :param int task_id: project.task record id
        :param dict post: post values
        """
        task = request.env["project.task"].search(
            [("id", "=", task_id), ("project_id", "=", project_id)]
        )
        if not task:
            raise MissingError(_("Task not found!"))
        if not task.check_portal_edit_access():
            raise AccessError(_("You are not allowed to edit this task."))
        values = self._task_action_page_view_values(task.project_id)
        values.update(
            {
                "task": task,
                "name": task.name,
                "description": task.description,
                "date_deadline": task.date_deadline,
                "button": _("Save"),
            }
        )
        if post and request.httprequest.method == "POST":
            error, error_message = self._validate_task_fields(post)
            if not error:
                task.write(self._prepare_task_values(post))
                return request.redirect(f"/my/projects/{project_id}/task/{task_id}")
            values.update({"error": error, "error_message": error_message, **post})
        values.update({"page_name": "task_edit"})
        return request.render(
            "project_task_create_portal.portal_project_task_new", values
        )

    def _project_get_page_view_values(
        self,
        project,
        access_token,
        page=1,
        date_begin=None,
        date_end=None,
        sortby=None,
        search=None,
        search_in="content",
        groupby=None,
        **kwargs,
    ):
        """Add portal task creation availability to project page values."""
        values = super()._project_get_page_view_values(
            project,
            access_token,
            page,
            date_begin,
            date_end,
            sortby,
            search,
            search_in,
            groupby,
            **kwargs,
        )
        # Access to visible create task button
        values[
            "searchbar_create_task"
        ] = project.sudo().is_portal_task_creation_allowed()
        return values

    def _task_get_searchbar_groupby(self, milestones_allowed):
        """Add task creator to the available portal grouping options."""
        values = super()._task_get_searchbar_groupby(milestones_allowed)
        values.update(
            create_uid={"input": "create_uid", "label": _("Created by"), "order": 12}
        )
        return dict(sorted(values.items(), key=lambda item: item[1]["order"]))

    def _task_get_searchbar_sortings(self, milestones_allowed):
        """Add task creator to the available portal sorting options."""
        values = super()._task_get_searchbar_sortings(milestones_allowed)
        values.update(
            create_uid={
                "label": _("Created by"),
                "order": "create_uid desc",
                "sequence": 12,
            }
        )
        return values

    def _task_get_groupby_mapping(self):
        """Map the portal creator grouping option to ``create_uid``."""
        result = super()._task_get_groupby_mapping()
        result.update(create_uid="create_uid")
        return result
