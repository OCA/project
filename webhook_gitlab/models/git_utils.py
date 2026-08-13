# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging
import re

from odoo import api, models

_logger = logging.getLogger(__name__)

DEFAULT_TASK_NAME_MATCH_REGEX = r"\b[A-Z][A-Z]+-\d+\b"
TASK_ID_REFERENCE_REGEX = r"\b(?:task|t)id#(?P<id>\d+)\b"


class GitUtils(models.AbstractModel):
    _name = "git.utils"
    _description = "Git Webhook Utilities"

    @api.model
    def _init_task_name_match_regex_param(self):
        """Seed the task_name_match_regex sysparam with the default pattern
        when missing."""
        config = self.env["ir.config_parameter"].sudo()
        if not config.get_param("webhook_gitlab.task_name_match_regex"):
            config.set_param(
                "webhook_gitlab.task_name_match_regex", DEFAULT_TASK_NAME_MATCH_REGEX
            )

    @api.model
    def _get_task_name_match_regex(self):
        """Fetch regex pattern from ir.config_parameter or fallback to default."""
        config = self.env["ir.config_parameter"].sudo()
        regex = config.get_param(
            "webhook_gitlab.task_name_match_regex",
            default=DEFAULT_TASK_NAME_MATCH_REGEX,
        )
        try:
            # Try compiling to validate the pattern
            re.compile(regex)
            return regex
        except re.error as e:
            _logger.warning(
                "Invalid task match regex in config parameter: %s."
                " Error: %s. Falling back to default.",
                regex,
                e,
            )
            return DEFAULT_TASK_NAME_MATCH_REGEX

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
