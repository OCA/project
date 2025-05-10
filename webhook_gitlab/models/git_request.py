# Copyright 2020, Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re
import logging

from urllib.parse import urljoin

import gitlab  # pylint: disable=W7935
from github import Github

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)

DEFAULT_TASK_NAME_SUBSTR_REGEX = r"\b[A-Z]+-\d+\b"


class GitRequest(models.Model):
    _name = "git.request"
    _description = "Information for Pull/Merge Requests"

    task_id = fields.Many2one("project.task", ondelete="cascade")
    id_request = fields.Integer(string="Request ID", help="Technical field used to track the merge request id")
    id_project = fields.Integer(
        string="Project ID",
        help="Technical field used to track the project id in Gitlab",
    )
    name = fields.Char(string="Title")
    wip = fields.Boolean(string="WIP")
    branch = fields.Char()
    last_commit = fields.Char()
    approved = fields.Boolean()
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
    url = fields.Char()
    user_id = fields.Many2one("res.users", string="Created by User")

    def open_merge_request(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_url",
            "url": self.url,
        }

    @api.model_create_multi
    def create(self, vals_list):
        rec = super().create(vals_list)
        rec.assing_tags()
        return rec

    def write(self, vals):
        res = super().write(vals)
        self.assing_tags()
        return res

    def assing_tags(self):
        for rec in self:
            tags = []
            record = rec.task_id
            tag_model = record.tag_ids._name
            current_tags = self.env[tag_model]
            current_tags |= record.tag_ids.filtered(lambda t: t.name.startswith("MR:") or t.name.startswith("CI:"))
            for tag in current_tags:
                tags.append((3, tag.id, 0))
            # Create prefix to have a base to get the external ID.
            # Possible values of prefix:
            # 'webhook_gitlab.project_tags_'
            prefix = "webhook_gitlab." + tag_model.replace(".", "_") + "_"
            # Get CI status tag.
            tags.append((4, self.env.ref(prefix + rec.ci_status).id, 0))
            # Get MR state tag.
            tags.append((4, self.env.ref(prefix + rec.state).id, 0))
            if rec.approved:
                tags.append((4, self.env.ref(prefix + "approved").id, 0))
            else:
                tags.append((3, self.env.ref(prefix + "approved").id, 0))
            if rec.wip:
                tags.append((4, self.env.ref(prefix + "wip").id, 0))
            else:
                tags.append((3, self.env.ref(prefix + "wip").id, 0))
            record.write(
                {
                    "tag_ids": tags,
                }
            )

    @api.model
    def _get_task_match_regex(self):
        """Fetch regex pattern from ir.config_parameter or fallback to default."""
        config = self.env["ir.config_parameter"].sudo()
        regex = config.get_param("webhook_gitlab.task_match_regex", default=DEFAULT_TASK_NAME_SUBSTR_REGEX)
        try:
            # Try compiling to validate the pattern
            re.compile(regex)
            return regex
        except re.error as e:
            _logger.warning("Invalid task match regex in config parameter: %s. Error: %s. Falling back to default.", regex, e)
            return DEFAULT_TASK_NAME_SUBSTR_REGEX

    @api.model
    def _get_record_type_and_id(self, title):
        """Searches in the title of the MR for the task ID with the
        correct format and returns the type of record and id if it can find it.

        :param title: Title of the MR
        :type: string
        :return: Dictionary with the type of record and ID obtained from the
        title or False if the title does not contain a correct format.
        :rtype: dictionary or boolean
        """
        exp = r"^(.*[ \(\[\<])?(?P<type>t(ask)?)#?(?P<id>\d+)([\)\]\>:=, \.,].*)?$"
        match = re.match(exp, title, re.IGNORECASE)
        if match:
            return match.groupdict()
        return False

    @api.model
    def _link_record(self, event, id_found):
        """Add link to GitLab to access Odoo task.
        Create the git.request related to task.
        """
        model = "project.task"
        rec_type = "task"
        record = self.env[model].sudo().browse(int(id_found["id"]))
        if not record:
            message = _(
                "The %(type)s #%(id)s cannot be found in Odoo.",
                type=rec_type,
                id=id_found["id"],
            )
            self._post_message(event, message)
            return False
        event_source = event.get("source", "gitlab")
        if event_source == "gitlab":
            project_id = event["project"]["id"]
            merge_request_id = event["object_attributes"]["iid"]
        else:
            project_id = event["repository"]["id"]
            merge_request_id = event["number"]
        git_request = self.sudo().search(
            [
                ("id_request", "=", merge_request_id),
                ("id_project", "=", project_id),
            ]
        )
        git_request_vals = self._prepare_git_request(record, event)
        if git_request:
            git_request.sudo().write(git_request_vals)
            return False
        git_request.sudo().create(git_request_vals)
        url = record._notify_get_action_link("view")
        message = _(
            "Linked to Odoo %(type)s [#%(id)s](%(url)s)",
            type=rec_type,
            id=record.id,
            url=url,
        )
        self._post_message(event, message)
        return True

    @api.model
    def _prepare_git_request(self, record, event):
        event_source = event.get("source", "gitlab")
        if event_source == "gitlab":
            vals = self._prepare_gilab_git_request(event)
        else:
            vals = self._prepare_github_git_request(event)
        if record._name == "project.task":
            vals["task_id"] = record.id
        return vals

    @api.model
    def _prepare_gilab_git_request(self, event):
        approved = False
        if event["object_attributes"]["action"] == "approved":
            approved = True
        user = self.env["res.users"].sudo().search([("gitlab_username", "=", event["user"]["username"])])
        return {
            "id_request": event["object_attributes"]["iid"],
            "id_project": event["project"]["id"],
            "name": event["object_attributes"]["title"],
            "wip": event["object_attributes"]["work_in_progress"],
            "state": event["object_attributes"]["state"],
            "approved": approved,
            "url": event["object_attributes"]["url"],
            "branch": event["object_attributes"]["source_branch"],
            "last_commit": event["object_attributes"]["last_commit"]["id"],
            "task_id": False,
            "user_id": user.id,
        }

    @api.model
    def _prepare_github_git_request(self, event):
        user = (
            self.env["res.users"]
            .sudo()
            .search(
                [
                    ("github_username", "=", event["pull_request"]["user"]["login"]),
                ]
            )
        )
        map_state = {
            "open": "opened",
            "closed": "closed",
            "merged": "merged",
        }
        return {
            "id_request": event["number"],
            "id_project": event["repository"]["id"],
            "name": event["pull_request"]["title"],
            "state": map_state[event["pull_request"]["state"]],
            "url": event["pull_request"]["html_url"],
            "branch": event["pull_request"]["head"]["ref"],
            "last_commit": event["pull_request"]["head"]["sha"],
            "task_id": False,
            "user_id": user.id,
        }

    @api.model
    def _process_merge_request(self, event):
        """Post messages in project.task based on the
        title of the Merge Request.
        The title must contain the type of registry and the ID preceded by a #
        sign.

        Ex. [IMP] webhook_gitlab: new module task#1234

        Also uses pattern matching to link MR resources to tasks.
        """
        # Original logic (unchanged)
        title = event["object_attributes"]["title"]
        id_found = self._get_record_type_and_id(title)
        if not id_found:
            message = self.env["ir.qweb"]._render("webhook_gitlab.gitlab_id_not_in_title")
            self._post_message(event, message)
        original_result = self._link_record(event, id_found)

        # New pattern matching logic
        repository_projects = self._get_related_projects_by_url(event=event)
        if repository_projects:
            # Extract MR data
            mr_data = event["object_attributes"]
            source_branch = mr_data.get("source_branch", "")
            mr_title = mr_data.get("title", "")

            # Find matching tasks using pattern matching
            matching_tasks = self.env["project.task"]

            # Try to match by source branch name first
            if source_branch:
                matching_tasks |= self._find_matching_tasks(projects=repository_projects, pattern_text=source_branch)

            # Also try to match by MR title
            if mr_title:
                matching_tasks |= self._find_matching_tasks(projects=repository_projects, pattern_text=mr_title)

            # Link MR resources to all matching tasks
            for task in matching_tasks:
                # Create git.pull.request record
                pr_data = event["object_attributes"]
                self._create_or_update_pull_request(task=task, pr_data=pr_data, event_source="gitlab")

                # Associate source branch
                source_branch = pr_data.get("source_branch", "")
                if source_branch:
                    self._create_or_update_branch(task=task, branch_name=source_branch, event=event)

                # If there's a last_commit, associate it
                if pr_data.get("last_commit"):
                    commit_data = pr_data["last_commit"]
                    self._create_or_update_commit(task=task, commit_data=commit_data, event_source="gitlab")

        return original_result

    @api.model
    def _process_pull_request(self, event):
        """Post messages in project.task based on the
        title of the Pull Request.
        The title must contain the type of registry and the ID preceded by a #
        sign.

        Ex. [IMP] webhook_gitlab: new module task#1234

        Also uses pattern matching to link PR resources to tasks.
        """
        # Original logic (unchanged)
        title = event["pull_request"]["title"]
        id_found = self._get_record_type_and_id(title)
        if not id_found:
            message = self.env["ir.qweb"]._render("webhook_gitlab.gitlab_id_not_in_title")
            self._post_message(event, message)
        original_result = self._link_record(event, id_found)

        # New pattern matching logic
        repository_projects = self._get_related_projects_by_url(event=event)
        if repository_projects:
            # Extract PR data (GitHub format)
            pr_data = event["pull_request"]
            source_branch = pr_data.get("head", {}).get("ref", "")
            pr_title = pr_data.get("title", "")

            # Find matching tasks using pattern matching
            matching_tasks = self.env["project.task"]

            # Try to match by source branch name first
            if source_branch:
                matching_tasks |= self._find_matching_tasks(projects=repository_projects, pattern_text=source_branch)

            # Also try to match by PR title
            if pr_title:
                matching_tasks |= self._find_matching_tasks(projects=repository_projects, pattern_text=pr_title)

            # Link PR resources to all matching tasks
            for task in matching_tasks:
                # Create git.pull.request record
                self._create_or_update_pull_request(task=task, pr_data=pr_data, event_source="github")

                # Associate source branch
                if source_branch:
                    self._create_or_update_branch(task=task, branch_name=source_branch, event=event)

                # Fetch all PR commits via GitHub API
                commits_url = pr_data.get("_links", {}).get("commits", {}).get("href", "")
                if commits_url:
                    pr_commits = self._fetch_github_pr_commits(commits_url=commits_url)
                    if pr_commits:
                        # Use all commits from API
                        self._link_commits_to_task(task=task, commits=pr_commits, event_source="github")
                    else:
                        # Fallback to HEAD commit if API call failed
                        head_sha = pr_data.get("head", {}).get("sha", "")
                        if head_sha:
                            commit_data = {
                                "id": head_sha,
                                "message": f"HEAD commit from PR: {pr_title}",
                                "url": f"{pr_data.get('html_url', '')}/commits/{head_sha}",
                                "timestamp": pr_data.get("updated_at", ""),
                            }
                            self._create_or_update_commit(task=task, commit_data=commit_data, event_source="github")
                else:
                    # Fallback to HEAD commit if no commits URL available
                    head_sha = pr_data.get("head", {}).get("sha", "")
                    if head_sha:
                        commit_data = {
                            "id": head_sha,
                            "message": f"HEAD commit from PR: {pr_title}",
                            "url": f"{pr_data.get('html_url', '')}/commits/{head_sha}",
                            "timestamp": pr_data.get("updated_at", ""),
                        }
                        self._create_or_update_commit(task, commit_data, "github")

        return original_result

    @api.model
    def _classify_push_event(self, event):
        """
        Classify push event type based on before/after SHA values.
        Returns: 'branch_creation', 'branch_deletion', 'commit_push', or 'unknown'
        """
        NULL_SHA = "0000000000000000000000000000000000000000"
        before = event.get("before", "")
        after = event.get("after", "")

        if before == NULL_SHA and after != NULL_SHA:
            return "branch_creation"
        elif before != NULL_SHA and after == NULL_SHA:
            return "branch_deletion"
        elif before != NULL_SHA and after != NULL_SHA:
            return "commit_push"
        else:
            return "unknown"

    @api.model
    def _get_branch_name_from_ref(self, ref):
        """Extract branch name from ref (e.g., 'refs/heads/feature-branch' -> 'feature-branch')"""
        if ref and ref.startswith("refs/heads/"):
            return ref.replace("refs/heads/", "")
        return ref

    @api.model
    def _find_matching_tasks(self, projects, pattern_text):
        """
        Find project tasks that match a given pattern in their name.
        Returns flat project.task recordset.
        """
        if not pattern_text:
            return self.env["project.task"]

        regex = self._get_task_match_regex()
        pattern_match = re.search(regex, pattern_text, re.IGNORECASE)
        if not pattern_match:
            return self.env["project.task"]

        pattern = pattern_match.group(0)
        matching_tasks = self.env["project.task"]

        for project in projects:
            for task in project.task_ids:
                if re.search(rf"\b{re.escape(pattern)}\b", task.name, re.IGNORECASE):
                    matching_tasks |= task

        return matching_tasks

    @api.model
    def _get_related_projects_by_url(self, event):
        """
        Get project.project records that match the repository URL from the event.
        Handles .git suffix variations automatically.
        Returns project.project recordset.
        """
        repository_url = event.get("repository_url", "")
        if not repository_url:
            return self.env["project.project"]

        # the response coming from git request might append ".git" suffix to the url
        # or the user might think that it's necessary to add the suffix: in order to
        # make the search consistent we always check for both variants
        if repository_url.endswith(".git"):
            urls_to_check = [repository_url, repository_url[:-4]]
        else:
            urls_to_check = [repository_url, f"{repository_url}.git"]

        repository_projects = self.env["project.project"].sudo().search([
            '|',
            ("git_project_url", "in", urls_to_check),
            ("git_dev_project_url", "in", urls_to_check)
        ])

        return repository_projects

    @api.model
    def _build_branch_url(self, event, branch_name):
        """
        Build branch URL based on event data and branch name.
        Returns branch URL string.
        """
        if not branch_name:
            return ""

        event_source = event.get("source", "gitlab")

        if event_source == "gitlab":
            web_url = event.get("project", {}).get("web_url", "")
            if web_url:
                # GitLab format: https://gitlab.com/owner/repo/-/tree/branch-name
                return f"{web_url}/-/tree/{branch_name}"
        elif event_source == "github":
            # Try to get from pull_request.head.repo first (PR events)
            html_url = event.get("pull_request", {}).get("head", {}).get("repo", {}).get("html_url", "")
            if not html_url:
                # Fallback to repository (push events)
                html_url = event.get("repository", {}).get("html_url", "")
            if html_url:
                # GitHub format: https://github.com/owner/repo/tree/branch-name
                return f"{html_url}/tree/{branch_name}"

        return ""

    @api.model
    def _create_or_update_commit(self, task, commit_data, event_source="gitlab"):
        """
        Create or update git.commit record. Avoids duplicates by checking SHA.
        Returns git.commit record.
        """
        full_sha = commit_data.get("id", "")
        if not full_sha:
            return self.env["git.commit"]

        existing_commit = self.env["git.commit"].sudo().search([
            ("full_sha", "=", full_sha),
            ("task_id", "=", task.id)
        ])

        if existing_commit:
            return existing_commit

        commit_vals = task._prepare_commit_vals(commit_data, event_source)
        new_commit = self.env["git.commit"].sudo().create(commit_vals)
        task.sudo().write({"git_commit_ids": [(4, new_commit.id)]})

        return new_commit

    @api.model
    def _create_or_update_branch(self, task, branch_name, event=None, branch_url=""):
        """
        Create or update git.branch record. Avoids duplicates by checking name+task.
        Returns git.branch record.
        """
        if not branch_name:
            return self.env["git.branch"]

        existing_branch = self.env["git.branch"].sudo().search([
            ("name", "=", branch_name),
            ("task_id", "=", task.id)
        ])

        if existing_branch:
            return existing_branch

        # Build branch URL if event is provided and no URL specified
        if not branch_url and event:
            branch_url = self._build_branch_url(event=event, branch_name=branch_name)

        branch_vals = {
            "name": branch_name,
            "url": branch_url,
            "task_id": task.id,
        }
        new_branch = self.env["git.branch"].sudo().create(branch_vals)
        task.sudo().write({"git_branch_ids": [(4, new_branch.id)]})

        return new_branch

    @api.model
    def _link_commits_to_task(self, task, commits, event_source="gitlab"):
        """
        Given a list of commits objects, create `git.commit` objects and
        link them to a task.
        """
        created_commits = self.env["git.commit"]
        for commit_data in commits:
            new_commit = self._create_or_update_commit(task=task, commit_data=commit_data, event_source=event_source)
            if new_commit:
                created_commits |= new_commit
        return created_commits

    @api.model
    def _create_or_update_pull_request(self, task, pr_data, event_source="gitlab"):
        """
        Create or update git.pull.request record. Avoids duplicates by checking URL.
        Returns git.pull.request record.
        """
        pr_url = pr_data.get("url", "") or pr_data.get("html_url", "")
        if not pr_url:
            return self.env["git.pull.request"]

        existing_pr = self.env["git.pull.request"].sudo().search([
            ("url", "=", pr_url),
            ("task_id", "=", task.id)
        ])

        if existing_pr:
            return existing_pr

        pr_vals = task._prepare_pull_request_vals(pr_data, event_source)
        new_pr = self.env["git.pull.request"].sudo().create(pr_vals)
        task.sudo().write({"git_pull_request_ids": [(4, new_pr.id)]})

        return new_pr

    @api.model
    def _fetch_github_pr_commits(self, commits_url):
        """
        Fetch all commits from a GitHub PR using the commits API endpoint.
        Returns list of commit data in GitHub API format.
        """
        try:
            github = self._connect_github()
            # Extract repo info and PR number from commits URL
            # URL format: https://api.github.com/repos/owner/repo/pulls/123/commits
            parts = commits_url.split("/")
            if len(parts) >= 7:
                owner = parts[-4]
                repo = parts[-3]
                pr_number = int(parts[-2])

                github_repo = github.get_repo(f"{owner}/{repo}")
                pr = github_repo.get_pull(pr_number)
                commits = list(pr.get_commits())

                # Convert PyGithub commit objects to our expected format
                commit_list = []
                for commit in commits:
                    commit_data = {
                        "id": commit.sha,
                        "message": commit.commit.message,
                        "url": commit.html_url,
                        "timestamp": commit.commit.author.date.isoformat() if commit.commit.author.date else "",
                    }
                    commit_list.append(commit_data)

                return commit_list
        except Exception as e:
            # Log error but don't fail - fallback will handle it
            _logger.warning(f"Failed to fetch GitHub PR commits from {commits_url}: {str(e)}")

        return []

    @api.model
    def _process_push(self, event):
        """
        Process push events with unified logic for:
        - Regular commit pushes
        - Branch creation
        - Branch deletion

        Links commits and branches to matching project tasks based on pattern matching.
        """

        repository_projects = self._get_related_projects_by_url(event=event)
        if not repository_projects:
            return

        event_source = event.get("source", "gitlab")
        push_type = self._classify_push_event(event=event)
        branch_name = self._get_branch_name_from_ref(ref=event.get("ref", ""))

        if push_type == "branch_creation":
            self._process_branch_creation(repository_projects, branch_name, event)
        elif push_type == "branch_deletion":
            self._process_branch_deletion(repository_projects, branch_name, event)
        elif push_type == "commit_push":
            self._process_commit_push(repository_projects, event, event_source)

    def _process_branch_creation(self, projects, branch_name, event):
        """Handle branch creation events"""
        if not branch_name:
            return

        # Find tasks matching branch name pattern
        matching_tasks = self._find_matching_tasks(projects=projects, pattern_text=branch_name)
        event_source = event.get("source", "gitlab")

        for task in matching_tasks:
            # Create branch
            self._create_or_update_branch(task=task, branch_name=branch_name, event=event)

            # If there are commits associated with branch creation, link them
            commits = event.get("commits", [])
            if commits:
                self._link_commits_to_task(task=task, commits=commits, event_source=event_source)

    def _process_branch_deletion(self, projects, branch_name, event):
        """Handle branch deletion events"""
        if not branch_name:
            return

        # Find existing branch records to potentially mark as deleted
        for project in projects:
            branches_to_delete = self.env["git.branch"].sudo().search([
                ("name", "=", branch_name),
                ("task_id.project_id", "=", project.id)
            ])
            for branch in branches_to_delete:
                # For now we keep the record but we could add a 'deleted' field later
                pass

    def _process_commit_push(self, projects, event, event_source):
        """
        Handle regular commit push events.

        Creates commits (and related branch if it doesn't exists)
        for tasks matching either branch name pattern or commit
        message pattern against project task name pattern.
        """
        commits = event.get("commits", [])
        if not commits:
            return

        branch_name = self._get_branch_name_from_ref(ref=event.get("ref", ""))

        matching_tasks = self.env["project.task"]

        if branch_name:
            matching_tasks |= self._find_matching_tasks(projects=projects, pattern_text=branch_name)

        for commit in commits:
            matching_tasks |= self._find_matching_tasks(projects=projects, pattern_text=commit.get("message", ""))

        for task in matching_tasks:
            self._create_or_update_commit(task=task, commit_data=commit, event_source=event_source)

            if branch_name:
                self._create_or_update_branch(task=task, branch_name=branch_name, event=event)

    @api.model
    def _process_pipeline(self, event):
        """Process pipeline status and update git.request in task.
        The title must contain the type of registry and the ID preceded by a #
        sign.

        Ex. [IMP] webhook_gitlab: new module task #1234
        """
        git_request = (
            self.env["git.request"]
            .sudo()
            .search(
                [
                    ("branch", "=", event["object_attributes"]["ref"]),
                    ("last_commit", "=", event["object_attributes"]["sha"]),
                ]
            )
        )

        if git_request:
            git_request.sudo().write(
                {
                    "ci_status": event["object_attributes"]["status"],
                }
            )
        return True

    @api.model
    def _connect_gitlab(self, event=None, url=None):
        """Connect to gitlab instance and return gitlab object"""
        if not url:
            url = event["project"]["web_url"]
        url = urljoin(url, "../..")
        token = self.env["ir.config_parameter"].sudo().get_param("webhook_gitlab.gitlab_token." + url)
        return gitlab.Gitlab(url, private_token=token)

    @api.model
    def _connect_github(self):
        """Connect to github instance and return github object"""
        token = self.env["ir.config_parameter"].sudo().get_param("webhook_gitlab.github_token")
        return Github(token)

    @api.model
    def _post_message(self, event, message):
        """Post a Message on Gitlab or Github"""
        event_source = event.get("source", "gitlab")
        if event_source == "gitlab":
            return self._post_gitlab_message(event, message)
        return self._post_github_message(event, message)

    @api.model
    def _post_github_message(self, event, message):
        """Post a message in the pull request of a project"""
        response = self._connect_github()
        repo = response.get_repo(event["repository"]["full_name"])
        pull = repo.get_pull(event["number"])
        pull.create_issue_comment(message)
        return True

    @api.model
    def _post_gitlab_message(self, event, message):
        """Post a message in the merge request of a project"""
        project_id = event["project"]["id"]
        merge_request_id = event["object_attributes"]["iid"]
        response = self._connect_gitlab(event)
        project = response.projects.get(project_id)
        merge_request = project.mergerequests.get(merge_request_id)
        merge_request.discussions.create({"body": message})
        return True
