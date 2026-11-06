# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import re

from odoo import api, models

TASK_NAME_MATCH_REGEX = r"\b[A-Z][A-Z]+-\d+\b"
TASK_ID_REFERENCE_REGEX = r"\b(?:task|t)id#(?P<id>\d+)\b"


class ProjectGitUtils(models.AbstractModel):
    _name = "project.git.utils"
    _description = "Project Git Webhook Utilities"

    @api.model
    def _get_task_name_match_regex(self):
        """Regex extracting issue keys from commit messages, branch names
        and PR/MR titles: Jira-strict keys such as "ABC-123". Extension
        hook: an override must keep the extracted keys free of LIKE
        wildcards (the task lookup prefilters candidates with ilike).
        """
        return TASK_NAME_MATCH_REGEX

    @api.model
    def _extract_task_id_references(self, text):
        """Extract the explicit task id references ("taskid#123" or
        "tid#123", case-insensitive) from a text. Every occurrence is
        considered.

        :param str text: any text carried by the event (PR/MR title,
            branch name, commit message)
        :return: list of referenced task ids
        :rtype: list(int)
        """
        if not text:
            return []
        return [
            int(task_id)
            for task_id in re.findall(TASK_ID_REFERENCE_REGEX, text, re.IGNORECASE)
        ]
