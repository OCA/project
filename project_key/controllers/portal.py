# Copyright 2026 Noviat
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo.http import request

from odoo.addons.project.controllers.portal import ProjectCustomerPortal


class ProjectKeyCustomerPortal(ProjectCustomerPortal):
    def _task_get_searchbar_inputs(self, milestones_allowed, project=False):
        values = super()._task_get_searchbar_inputs(milestones_allowed, project)
        values["key"] = {
            "input": "key",
            "label": request.env._("Search in Key"),
            "sequence": 15,
        }
        return values

    def _task_get_search_domain(self, search_in, search, milestones_allowed, project):
        if search_in == "key":
            return [("key", "ilike", search)]
        return super()._task_get_search_domain(
            search_in, search, milestones_allowed, project
        )
