# Copyright 2020, Jarsa
# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class ProjectGitPullRequest(models.Model):
    _name = "project.git.pull.request"
    _description = "Git Pull/Merge Request"

    name = fields.Char(string="Title")
    description = fields.Text()
    url = fields.Char(string="PR/MR URL")

    id_request = fields.Integer(
        string="Request ID", help="Technical field used to track the merge request id"
    )
    id_project = fields.Integer(
        string="Project ID",
        help="Technical field used to track the project id on the platform",
    )
    # Each platform bridge adds its own value with selection_add
    source = fields.Selection([], string="Source Platform")

    source_branch = fields.Char()
    target_branch = fields.Char()
    source_branch_id = fields.Many2one(
        comodel_name="project.git.branch",
        string="Source Branch Record",
        help="The tracked branch record of the source branch, when "
        "the branch is tracked in Odoo (target branches are never "
        "tracked, so they stay as plain names).",
    )

    state = fields.Selection(
        [
            ("opened", "Opened"),
            ("merged", "Merged"),
            ("closed", "Closed"),
            ("locked", "Locked"),
        ]
    )
    ci_status = fields.Selection(
        [
            ("pending", "Pending"),
            ("running", "Running"),
            ("success", "Success"),
            ("failed", "Failed"),
            ("skipped", "Skipped"),
            ("canceled", "Canceled"),
            ("unknown", "Unknown"),
        ],
        string="CI Status",
    )

    wip = fields.Boolean(string="WIP")
    approved = fields.Boolean()

    last_commit = fields.Char()
    user_id = fields.Many2one("res.users", string="Created by User")

    task_ids = fields.Many2many(
        comodel_name="project.task",
        relation="project_git_pull_request_task_rel",
        column1="pull_request_id",
        column2="task_id",
        string="Related Tasks",
    )
    notified_task_ids = fields.Many2many(
        comodel_name="project.task",
        relation="project_git_pull_request_notified_task_rel",
        column1="pull_request_id",
        column2="task_id",
        string="Notified Tasks",
        help="Tasks whose link has already been posted as a message on the "
        "PR/MR, used to avoid posting the same task link twice.",
    )

    git_commit_ids = fields.Many2many(
        comodel_name="project.git.commit",
        relation="project_git_pull_request_commit_rel",
        column1="pull_request_id",
        column2="commit_id",
        string="Commits",
    )

    _sql_constraints = [
        (
            "source_project_request_unique",
            "unique(source, id_project, id_request)",
            "A pull request with the same identifiers is already tracked"
            " for this platform.",
        )
    ]

    def open_merge_request(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_url",
            "url": self.url,
        }

    @api.model_create_multi
    def create(self, vals_list):
        rec = super().create(vals_list)
        rec.assign_tags()
        return rec

    def write(self, vals):
        res = super().write(vals)
        self.assign_tags()
        return res

    def _post_task_link_messages(self, event):
        """Post a message on the PR/MR with the link to each related task.

        Already notified tasks are tracked in notified_task_ids so that
        each task link is posted only once per pull request (avoids message
        spam, since PR/MR events fire on every update).

        :param dict event: The webhook event (passed down to the
            per-source _post_message implementations, e.g. for the
            platform connection)
        :return: recordset of the tasks notified by this call
        """
        self.ensure_one()
        git_pull_request = self.sudo()
        tasks_to_notify = git_pull_request.task_ids - git_pull_request.notified_task_ids
        for task in tasks_to_notify:
            url = task._notify_get_action_link("view")
            message = _(
                "Linked to Odoo task [#%(id)s](%(url)s)",
                id=task.id,
                url=url,
            )
            git_pull_request._post_message(message, event)
        if tasks_to_notify:
            git_pull_request.notified_task_ids = [
                (4, task.id) for task in tasks_to_notify
            ]
        return tasks_to_notify

    @api.model
    def _is_pr_opening_or_title_change(self, event):
        """Return True when the PR/MR is being opened or its title edited.

        These are the only moments when title-based feedback is
        actionable: PR/MR events fire on every update, so negative-result
        messages must not be reposted each time.

        The title change check (changes.title) is common to every
        platform; the opening detection is per-source.
        """
        is_opening = False
        if hasattr(self, "_is_pr_opening_%s" % event.get("source")):
            is_opening = getattr(self, "_is_pr_opening_%s" % event.get("source"))(event)
        title_changed = bool(event.get("changes", {}).get("title"))
        return is_opening or title_changed

    @api.model
    def _post_negative_match_messages(
        self, event, matching_tasks, title_task_references, repository_projects
    ):
        """Warn on the PR/MR about broken or missing task references.

        - explicit "taskid#<id>" title reference(s) to tasks that do not
          exist;
        - no task reference at all (only for repositories related to an
          Odoo project, to avoid commenting unrelated repositories).
        Posted only on PR opening or title change (anti-spam). Model
        method: in these cases the PR/MR is usually not tracked in Odoo,
        so the message posting relies on the event for identification.

        :param list(int) title_task_references: task ids referenced in
            the PR/MR title (see
            project.git.utils._extract_task_id_references)
        """
        if not self._is_pr_opening_or_title_change(event):
            return
        missing_task_ids = [
            task_id
            for task_id in title_task_references
            if not self.env["project.task"].sudo().browse(task_id).exists()
        ]
        if missing_task_ids:
            message = _(
                "The task id(s) %(ids)s cannot be found in Odoo.",
                ids=", ".join(f"#{task_id}" for task_id in missing_task_ids),
            )
            self._post_message(message, event)
        elif not matching_tasks and repository_projects:
            message = self.env["ir.qweb"]._render(
                "project_git.no_task_reference_in_title"
            )
            self._post_message(message, event)

    def _post_message(self, message, event=None):
        """Post a message on the PR/MR on its source platform.

        Works either on a single record (its fields identify the PR/MR)
        or on an empty recordset with the event as identification
        fallback (e.g. warnings for PRs not tracked in Odoo). The
        per-source implementations live in the platform bridges.
        """
        if self:
            self.ensure_one()
            source = self.source
        else:
            source = (event or {}).get("source")
        if hasattr(self, "_post_message_%s" % source):
            return getattr(self, "_post_message_%s" % source)(message, event)
        _logger.warning("No _post_message implementation for source %r", source)
        return False

    def assign_tags(self):
        for git_pull_request in self:
            if not git_pull_request.state:
                continue
            for task in git_pull_request.task_ids:
                git_pull_request._assign_tags_to_task(task)

    def _assign_tags_to_task(self, task):
        """Align the MR/CI state tags of a single related task."""
        self.ensure_one()
        tags = []
        tag_model = task.tag_ids._name
        current_tags = self.env[tag_model]
        current_tags |= task.tag_ids.filtered(
            lambda t: t.name.startswith("MR:") or t.name.startswith("CI:")
        )
        for tag in current_tags:
            tags.append((3, tag.id, 0))
        # Create prefix to have a base to get the external ID.
        # Possible values of prefix:
        # 'project_git.project_tags_'
        prefix = "project_git." + tag_model.replace(".", "_") + "_"
        # Get CI status tag.
        if self.ci_status:
            tags.append((4, self.env.ref(prefix + self.ci_status).id, 0))
        # Get MR state tag.
        tags.append((4, self.env.ref(prefix + self.state).id, 0))
        if self.approved:
            tags.append((4, self.env.ref(prefix + "approved").id, 0))
        else:
            tags.append((3, self.env.ref(prefix + "approved").id, 0))
        if self.wip:
            tags.append((4, self.env.ref(prefix + "wip").id, 0))
        else:
            tags.append((3, self.env.ref(prefix + "wip").id, 0))
        task.write(
            {
                "tag_ids": tags,
            }
        )
