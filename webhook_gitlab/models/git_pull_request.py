# Copyright 2020, Jarsa
# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models


class GitPullRequest(models.Model):
    _name = "git.pull.request"
    _description = "Git Pull/Merge Request"

    name = fields.Char(string="Title")
    description = fields.Text(string="Description")
    url = fields.Char(string="PR/MR URL")

    id_request = fields.Integer(
        string="Request ID",
        help="Technical field used to track the merge request id"
    )
    id_project = fields.Integer(
        string="Project ID",
        help="Technical field used to track the project id in Gitlab",
    )
    source = fields.Selection(
        [("gitlab", "GitLab"), ("github", "GitHub")],
        string="Source Platform"
    )

    source_branch = fields.Char(string="Source Branch")
    target_branch = fields.Char(string="Target Branch")
    source_branch_id = fields.Many2one(
        comodel_name="git.branch",
        string="Source Branch Record",
        help="The tracked git.branch record of the source branch, when "
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
        default="pending",
        string="CI Status",
    )

    wip = fields.Boolean(string="WIP")
    approved = fields.Boolean()

    last_commit = fields.Char()
    user_id = fields.Many2one("res.users", string="Created by User")

    task_ids = fields.Many2many(
        comodel_name="project.task",
        relation="git_pull_request_project_task_rel",
        column1="git_pull_request_id",
        column2="project_task_id",
        string="Related Tasks",
    )
    notified_task_ids = fields.Many2many(
        comodel_name="project.task",
        relation="git_pull_request_notified_task_rel",
        column1="git_pull_request_id",
        column2="project_task_id",
        string="Notified Tasks",
        help="Tasks whose link has already been posted as a message on the "
             "PR/MR, used to avoid posting the same task link twice.",
    )

    git_commit_ids = fields.Many2many(
        comodel_name="git.commit",
        relation="git_pull_request_git_commit_rel",
        column1="git_pull_request_id",
        column2="git_commit_id",
        string="Commits",
    )

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

        :param dict event: The webhook event (needed for the GitLab connection)
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
            git_pull_request.notified_task_ids = [(4, task.id) for task in tasks_to_notify]
        return tasks_to_notify

    @api.model
    def _is_pr_opening_or_title_change(self, event):
        """Return True when the PR/MR is being opened or its title edited.

        These are the only moments when title-based feedback is
        actionable: PR/MR events fire on every update, so negative-result
        messages must not be reposted each time.
        """
        event_source = event.get("source", "gitlab")
        if event_source == "gitlab":
            is_opening = event.get("object_attributes", {}).get("action") == "open"
        else:
            is_opening = event.get("action") == "opened"
        title_changed = bool(event.get("changes", {}).get("title"))
        return is_opening or title_changed

    @api.model
    def _post_negative_match_messages(self, event, matching_tasks, id_found, repository_projects):
        """Warn on the PR/MR about broken or missing task references.

        - explicit "task#<id>" reference to a task that does not exist;
        - no task reference at all (only for repositories related to an
          Odoo project, to avoid commenting unrelated repositories).
        Posted only on PR opening or title change (anti-spam). Model
        method: in these cases the PR/MR is usually not tracked in Odoo,
        so the message posting relies on the event for identification.
        """
        if not self._is_pr_opening_or_title_change(event):
            return
        if id_found and not self.env["project.task"].sudo().browse(int(id_found["id"])).exists():
            message = _(
                "The task #%(id)s cannot be found in Odoo.",
                id=id_found["id"],
            )
            self._post_message(message, event)
        elif not matching_tasks and repository_projects:
            message = self.env["ir.qweb"]._render("webhook_gitlab.no_task_reference_in_title")
            self._post_message(message, event)

    def _post_message(self, message, event=None):
        """Post a message on the PR/MR on its source platform.

        Works either on a single record (its fields identify the PR/MR)
        or on an empty recordset with the event as identification
        fallback (e.g. warnings for PRs not tracked in Odoo). On GitLab
        the event is also needed to derive the instance base URL for the
        API connection.
        """
        if self:
            self.ensure_one()
            source = self.source
        else:
            source = (event or {}).get("source", "gitlab")
        if source == "gitlab":
            return self._post_gitlab_message(message, event)
        return self._post_github_message(message, event)

    def _post_github_message(self, message, event=None):
        """Post a comment on the GitHub pull request"""
        if self:
            self.ensure_one()
            repository_id, request_id = self.id_project, self.id_request
        else:
            repository_id = event["repository"]["id"]
            request_id = event["number"]
        github = self.env["git.event"]._connect_github()
        repo = github.get_repo(repository_id)
        pull = repo.get_pull(request_id)
        pull.create_issue_comment(message)
        return True

    def _post_gitlab_message(self, message, event=None):
        """Post a comment (discussion) on the GitLab merge request.

        The event, when available, is the preferred source for the GitLab
        instance base URL (project.web_url is authoritative on any GitLab
        version). Without an event the URL falls back to the record MR
        URL, assuming the modern ``/-/merge_requests/`` layout.
        """
        if self:
            self.ensure_one()
            project_id, request_id = self.id_project, self.id_request
        else:
            project_id = event["project"]["id"]
            request_id = event["object_attributes"]["iid"]
        web_url = event["project"]["web_url"] if event else self.url.split("/-/")[0]
        gitlab_client = self.env["git.event"]._connect_gitlab(url=web_url)
        project = gitlab_client.projects.get(project_id)
        merge_request = project.mergerequests.get(request_id)
        merge_request.discussions.create({"body": message})
        return True

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
        current_tags |= task.tag_ids.filtered(lambda t: t.name.startswith("MR:") or t.name.startswith("CI:"))
        for tag in current_tags:
            tags.append((3, tag.id, 0))
        # Create prefix to have a base to get the external ID.
        # Possible values of prefix:
        # 'webhook_gitlab.project_tags_'
        prefix = "webhook_gitlab." + tag_model.replace(".", "_") + "_"
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
