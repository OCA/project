# Copyright 2020, Jarsa
# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re
import logging

from urllib.parse import urljoin

import gitlab  # pylint: disable=W7935
from github import Github

from odoo import _, api, fields, models
from odoo.tools import str2bool

_logger = logging.getLogger(__name__)

DEFAULT_TASK_NAME_SUBSTR_REGEX = r"\b[A-Z]+-\d+\b"


class GitEvent(models.Model):
    _name = "git.event"
    _description = "Git Webhook Event Processor"

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
        Create the git.pull.request related to task.
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

        # Search for existing pull request
        git_pull_request = self.env["git.pull.request"].sudo().search(
            [
                ("id_request", "=", merge_request_id),
                ("id_project", "=", project_id),
            ]
        )

        if git_pull_request:
            # Update existing PR (task_id passed via values)
            git_pull_request.sudo().write(
                self._prepare_pull_request_vals(event, values={"task_id": record.id})
            )
            return False

        # Create new PR
        self._create_or_update_pull_request(
            event=event,
            values={"task_id": record.id}
        )

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
        if id_found:
            result = self._link_record(event, id_found)
        else:
            message = self.env["ir.qweb"]._render("webhook_gitlab.gitlab_id_not_in_title")
            self._post_message(event, message)
            result = False

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
                self._create_or_update_pull_request(
                    event=event,
                    values={"task_id": task.id}
                )

                # Associate source branch
                self._create_or_update_branch(
                    event=event,
                    values={"task_id": task.id}
                )

                # If there's a last_commit, associate it
                if mr_data.get("last_commit"):
                    commit_data = mr_data["last_commit"]
                    self._create_or_update_commit(
                        commit_data=commit_data,
                        event=event,
                        values={"task_id": task.id}
                    )

        return result

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
        if id_found:
            result = self._link_record(event, id_found)
        else:
            message = self.env["ir.qweb"]._render("webhook_gitlab.gitlab_id_not_in_title")
            self._post_message(event, message)
            result = False

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
                self._create_or_update_pull_request(
                    event=event,
                    values={"task_id": task.id}
                )

                # Associate source branch
                self._create_or_update_branch(
                    event=event,
                    values={"task_id": task.id}
                )

                # Fetch all PR commits via GitHub API
                commits_url = pr_data.get("_links", {}).get("commits", {}).get("href", "")
                if commits_url:
                    pr_commits = self._fetch_github_pr_commits(commits_url=commits_url)
                    if pr_commits:
                        # Use all commits from API
                        self._link_commits_to_task(task=task, commits=pr_commits, event=event)
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
                            self._create_or_update_commit(
                                commit_data=commit_data,
                                event=event,
                                values={"task_id": task.id}
                            )
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
                        self._create_or_update_commit(
                            commit_data=commit_data,
                            event=event,
                            values={"task_id": task.id}
                        )

        return result

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
        """Extract branch name from ref (e.g., 'refs/heads/feature-branch' -> 'feature-branch')

        DEPRECATED: Use _extract_branch_names_from_event() instead for more flexibility.
        This method is kept for backward compatibility.
        """
        if ref and ref.startswith("refs/heads/"):
            return ref.replace("refs/heads/", "")
        return ref

    @api.model
    def _extract_branch_names_from_event(self, event):
        """Extract source and target branch names from event based on event type and source.

        Returns dict with:
        - source_branch: The branch where changes come from (or the only branch for push events)
        - target_branch: The branch where changes go to (only for MR/PR events, empty string otherwise)

        :param dict event: The webhook event
        :return: dict with 'source_branch' and 'target_branch' keys (empty strings if not present)
        """
        event_source = event.get("source", "gitlab")
        result = {
            "source_branch": "",
            "target_branch": "",
        }

        # Check if it's a MR/PR event (has both source and target branches)
        if event_source == "gitlab" and "object_attributes" in event:
            # GitLab Merge Request
            obj_attrs = event.get("object_attributes", {})
            result["source_branch"] = obj_attrs.get("source_branch", "")
            result["target_branch"] = obj_attrs.get("target_branch", "")
        elif event_source == "github" and "pull_request" in event:
            # GitHub Pull Request
            pr_data = event.get("pull_request", {})
            result["source_branch"] = pr_data.get("head", {}).get("ref", "")
            result["target_branch"] = pr_data.get("base", {}).get("ref", "")
        elif "ref" in event:
            # Push event (branch creation/deletion/commit push)
            # Extract branch name from ref (e.g., 'refs/heads/feature' -> 'feature')
            ref = event.get("ref", "")
            if ref and ref.startswith("refs/heads/"):
                branch_name = ref.replace("refs/heads/", "")
            else:
                branch_name = ref
            result["source_branch"] = branch_name
            # No target_branch for push events

        return result

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

        :param dict event: The webhook event
        :param str branch_name: Branch name (required)
        :return: branch URL string (empty string if cannot be built)

        Note: This method intentionally requires branch_name as explicit arg
        to avoid ambiguity in PR/MR events (which have 2 branches: source
        and destination). For more flexibility, it could call
        _extract_branch_names_from_event locally and accept a branch_type
        arg ('source'/'target') or return both URLs in a dict, but this
        was avoided to keep the API simple and unambiguous.
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
    def _create_or_update_commit(self, commit_data, event, values=None, update_existing=True):
        """
        Create or update a git.commit from commit data.

        The commit is identified by full_sha (globally unique).
        If task_id is provided in values, the commit will be linked to that task.

        :param dict commit_data: commit data with 'id' (full SHA), 'message', 'url', etc.
        :param dict event: The webhook event (used to extract event_source)
        :param dict values: Optional dict with additional values (e.g. task_id)
        :param bool update_existing: update existing commit if found
        :return: git.commit record
        """
        full_sha = commit_data.get("id", "")
        if not full_sha:
            return self.env["git.commit"]

        values_by_arg = values or {}

        # Prepare default values (task_id passed via values_by_arg)
        create_or_upd_vals = self._prepare_commit_vals(
            commit_data=commit_data,
            event=event,
            values=values_by_arg
        )

        # Get task
        task_id = create_or_upd_vals.get("task_id")
        task = self.env["project.task"].sudo().browse(task_id) if task_id else self.env["project.task"]

        # Search existing commit by full_sha (globally unique)
        existing_commit = self._search_existing_commit(commit_data=commit_data)

        # Update if exists
        if existing_commit and update_existing:
            existing_commit.sudo().write(create_or_upd_vals)

        # Create if not exists
        if not existing_commit:
            if not task:
                create_without_task = str2bool(
                    self.env["ir.config_parameter"].sudo().get_param(
                        "webhook_gitlab.option_create_without_task_match",
                        default="True"
                    )
                )
                if not create_without_task:
                    # Don't create commit without task association
                    return self.env["git.commit"]
            new_commit = self.env["git.commit"].sudo().create(create_or_upd_vals)

        git_commit = existing_commit or new_commit

        if task and git_commit.id not in task.git_commit_ids.ids:
            # Link to task
            task.write({"git_commit_ids": [(4, git_commit.id)]})

        return git_commit

    @api.model
    def _create_or_update_branch(self, event, values=None, update_existing=True):
        """
        Create or update a git.branch from event.

        If task_id is provided in values, the branch will be linked to that task.

        :param dict event: The webhook event
        :param dict values: Optional dict with additional values (can include "name", "url", "task_id")
        :param bool update_existing: update existing branch if found
        :return: git.branch record
        """
        values_by_arg = values or {}

        # Get branch_name from values or extract from event
        branch_name = values_by_arg.get("name")
        if not branch_name:
            # Extract from event using helper
            branch_names = self._extract_branch_names_from_event(event)
            branch_name = branch_names["source_branch"]

        if not branch_name:
            return self.env["git.branch"]

        # Build branch URL if no URL in values
        branch_url = values_by_arg.get("url", "")
        if not branch_url:
            branch_url = self._build_branch_url(event=event, branch_name=branch_name)

        default_vals = {
            "name": branch_name,
            "url": branch_url,
        }

        create_or_upd_vals = {**default_vals, **values_by_arg}

        task_id = create_or_upd_vals.get("task_id")
        task = self.env["project.task"].sudo().browse(task_id) if task_id else self.env["project.task"]

        # Search existing by URL (unique identifier)
        existing_branch = self._search_existing_branch(
            branch_url=branch_url,
            event=event
        )

        if existing_branch and update_existing:
            existing_branch.sudo().write(create_or_upd_vals)


        if not existing_branch:
            if not task:
                create_without_task = str2bool(
                    self.env["ir.config_parameter"].sudo().get_param(
                        "webhook_gitlab.option_create_without_task_match",
                        default="True"
                    )
                )
                if not create_without_task:
                    # Don't create branch without task association
                    return self.env["git.branch"]
            new_branch = self.env["git.branch"].sudo().create(create_or_upd_vals)

        git_branch = existing_branch or new_branch

        # Link to task
        if task and git_branch.id not in task.git_branch_ids.ids:
                task.write({"git_branch_ids": [(4, git_branch.id)]})

        return git_branch

    @api.model
    def _link_commits_to_task(self, task, commits, event):
        """
        Given a list of commits objects and the event, create `git.commit` objects and
        link them to a task.
        """
        created_commits = self.env["git.commit"]
        for commit_data in commits:
            new_commit = self._create_or_update_commit(
                commit_data=commit_data,
                event=event,
                values={"task_id": task.id}
            )
            if new_commit:
                created_commits |= new_commit
        return created_commits

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

        push_type = self._classify_push_event(event=event)

        if push_type == "branch_creation":
            self._process_branch_creation(repository_projects, event)
        elif push_type == "branch_deletion":
            self._process_branch_deletion(repository_projects, event)
        elif push_type == "commit_push":
            self._process_commit_push(repository_projects, event)

    def _process_branch_creation(self, projects, event):
        """Handle branch creation events"""
        # Extract branch name from event
        branch_names = self._extract_branch_names_from_event(event)
        branch_name = branch_names["source_branch"]
        if not branch_name:
            return

        # Find tasks matching branch name pattern
        matching_tasks = self._find_matching_tasks(projects=projects, pattern_text=branch_name)

        for task in matching_tasks:
            # Create branch
            self._create_or_update_branch(
                event=event,
                values={"task_id": task.id}
            )

            # If there are commits associated with branch creation, link them
            commits = event.get("commits", [])
            if commits:
                self._link_commits_to_task(task=task, commits=commits, event=event)

    def _process_branch_deletion(self, projects, event):
        """Handle branch deletion events"""
        # Extract branch name from event
        branch_names = self._extract_branch_names_from_event(event)
        branch_name = branch_names["source_branch"]
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

    def _process_commit_push(self, projects, event):
        """
        Handle regular commit push events.

        Creates commits (and related branch if it doesn't exists)
        for tasks matching either branch name pattern or commit
        message pattern against project task name pattern.
        """
        commits = event.get("commits", [])
        if not commits:
            return

        branch_names = self._extract_branch_names_from_event(event)
        branch_name = branch_names["source_branch"]

        matching_tasks = self.env["project.task"]

        if branch_name:
            # also check branch pattern match will cover following case:
            # pattern not found in any commit message, or pattern found
            # but no task matching. But, a pattern is found in branch
            # name and it also matches with task ID or name, in this case
            # we still link all pushed commit to the matching task
            matching_tasks |= self._find_matching_tasks(projects=projects, pattern_text=branch_name)

        for commit in commits:
            matching_tasks |= self._find_matching_tasks(projects=projects, pattern_text=commit.get("message", ""))

        # found all matching tasks, now create pushed commit if they doesn't exist yet and link all of them
        # to all the matching tasks
        for task in matching_tasks:
            for commit_data in commits:
                self._create_or_update_commit(
                    commit_data=commit_data,
                    event=event,
                    values={"task_id": task.id}
                )

            self._create_or_update_branch(
                event=event,
                values={"task_id": task.id}
            ) # todo move _create_or_update_branch inside _create_or_update_commit

    @api.model
    def _process_pipeline(self, event):
        """Process pipeline status and update git.pull.request.
        The title must contain the type of registry and the ID preceded by a #
        sign.

        Ex. [IMP] webhook_gitlab: new module task #1234
        """
        git_pull_request = (
            self.env["git.pull.request"]
            .sudo()
            .search(
                [
                    ("source_branch", "=", event["object_attributes"]["ref"]),
                    ("last_commit", "=", event["object_attributes"]["sha"]),
                ]
            )
        )

        if git_pull_request:
            git_pull_request.sudo().write(
                {
                    "ci_status": event["object_attributes"]["status"],
                }
            )
        return True

    @api.model
    def _prepare_commit_vals(self, commit_data, event, values=None):
        """Prepare commit values from commit data.

        :param dict commit_data: commit data with 'id', 'message', 'url', 'timestamp', etc.
        :param dict event: The webhook event (used to extract event source)
        :param dict values: Optional dict with values to override/merge (e.g. "task_id")
        :return: dict of commit values ready for create/write
        """
        values_by_arg = values or {}

        # Extract event source from event
        event_source = event.get("source", "gitlab")

        default_vals = {}
        timestamp = self.env["git.commit"].parse_timestamp(commit_data.get("timestamp", ""))

        if event_source == "gitlab":
            default_vals.update({
                "name": commit_data.get("title", ""),
                "description": commit_data.get("message", ""),
                "url": commit_data.get("url", ""),
                "full_sha": commit_data.get("id", ""),
                "timestamp": timestamp,
            })
        elif event_source == "github":
            commit_text_lines = commit_data.get("message", "").split("\n", 1)
            commit_title = commit_text_lines[0][:60]
            commit_description = commit_text_lines[1] if len(commit_text_lines) > 1 else ""
            default_vals.update({
                "name": commit_title,
                "description": commit_description,
                "url": commit_data.get("url", ""),
                "full_sha": commit_data.get("id", ""),
                "timestamp": timestamp,
            })

        # Merge with values_by_arg (task_id, etc.)
        return {**default_vals, **values_by_arg}

    @api.model
    def _prepare_branch_vals(self, event, values=None):
        """Prepare branch values from event.

        Extracts branch name and URL from event using helpers if not provided in values.

        :param dict event: The webhook event
        :param dict values: Optional dict with values to override/merge (e.g. "name", "url", "task_id")
        :return: dict of branch values ready for create/write
        """
        values_by_arg = values or {}

        # Get name from values or extract from event
        branch_name = values_by_arg.get("name")
        if not branch_name:
            branch_names = self._extract_branch_names_from_event(event)
            branch_name = branch_names["source_branch"]

        # Get URL from values or build from event
        branch_url = values_by_arg.get("url")
        if not branch_url:
            branch_url = self._build_branch_url(event=event, branch_name=branch_name)

        # Build base vals
        default_vals = {
            "name": branch_name,
            "url": branch_url,
        }

        # Merge with values_by_arg (task_id, etc.)
        return {**default_vals, **values_by_arg}

    @api.model
    def _prepare_gitlab_pull_request(self, event, values=None):
        """Prepare GitLab merge request values from event.

        :param dict event: The webhook event
        :param dict values: Optional dict with values to override/merge (e.g. "task_id")
        :return: dict of pull request values ready for create/write
        """
        values_by_arg = values or {}

        approved = False
        if event["object_attributes"]["action"] == "approved":
            approved = True
        user = self.env["res.users"].sudo().search([("gitlab_username", "=", event["user"]["username"])])

        default_vals = {
            "id_request": event["object_attributes"]["iid"],
            "id_project": event["project"]["id"],
            "source": "gitlab",
            "name": event["object_attributes"]["title"],
            "description": event["object_attributes"].get("description", ""),
            "url": event["object_attributes"]["url"],
            "source_branch": event["object_attributes"]["source_branch"],
            "target_branch": event["object_attributes"]["target_branch"],
            "wip": event["object_attributes"]["work_in_progress"],
            "state": event["object_attributes"]["state"],
            "approved": approved,
            "last_commit": event["object_attributes"]["last_commit"]["id"],
            "user_id": user.id,
        }

        # Merge with values_by_arg (task_id, etc.)
        return {**default_vals, **values_by_arg}

    @api.model
    def _prepare_github_pull_request(self, event, values=None):
        """Prepare GitHub pull request values from event.

        :param dict event: The webhook event
        :param dict values: Optional dict with values to override/merge (e.g. "task_id")
        :return: dict of pull request values ready for create/write
        """
        values_by_arg = values or {}

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

        default_vals = {
            "id_request": event["number"],
            "id_project": event["repository"]["id"],
            "source": "github",
            "name": event["pull_request"]["title"],
            "description": event["pull_request"].get("body", ""),
            "url": event["pull_request"]["html_url"],
            "source_branch": event["pull_request"]["head"]["ref"],
            "target_branch": event["pull_request"]["base"]["ref"],
            "state": map_state[event["pull_request"]["state"]],
            "last_commit": event["pull_request"]["head"]["sha"],
            "user_id": user.id,
        }

        # Merge with values_by_arg (task_id, etc.)
        return {**default_vals, **values_by_arg}

    @api.model
    def _prepare_pull_request_vals(self, event, values=None):
        """Prepare git.pull.request values based on event source.

        :param dict event: The webhook event
        :param dict values: Optional dict with values to override/merge (e.g. "task_id")
        :return: dict of pull request values ready for create/write
        """
        values = values or {}
        event_source = event.get("source", "gitlab")
        if event_source == "gitlab":
            return self._prepare_gitlab_pull_request(event, values=values)
        elif event_source == "github":
            return self._prepare_github_pull_request(event, values=values)
        return values

    @api.model
    def _search_existing_pull_request(self, event):
        """Search for existing pr by id_request/id_project (might check by url)
        :param dict event: git event
        :return: existing pull request or empty recordset"""
        git_pull_request = self.env["git.pull.request"]
        event_source = event.get("source", "gitlab")
        if event_source == "gitlab":
            project_id = event["project"]["id"]
            request_id = event["object_attributes"]["iid"]
        else:
            project_id = event["repository"]["id"]
            request_id = event["number"]

        git_pull_request = self.env["git.pull.request"].sudo().search([
            ("id_request", "=", request_id),
            ("id_project", "=", project_id),
        ], limit=1)
        return git_pull_request

    @api.model
    def _search_existing_commit(self, commit_data):
        """Search for existing commit by full SHA (globally unique).

        :param dict commit_data: commit data containing 'id' (full SHA)
        :return: existing commit or empty recordset
        """
        full_sha = commit_data.get("id", "")
        if not full_sha:
            return self.env["git.commit"]

        return self.env["git.commit"].sudo().search([
            ("full_sha", "=", full_sha)
        ], limit=1)

    @api.model
    def _search_existing_branch(self, branch_url=None, event=None):
        """Search for existing branch by URL (unique identifier only).

        If branch_url is not provided, attempts to extract and build it from event.

        :param str branch_url: branch URL (optional, unique identifier)
        :param dict event: optional event to extract branch data from
        :return: existing branch or empty recordset
        """
        # Get URL from parameter or extract from event
        url_to_search = branch_url
        if not url_to_search and event:
            # Extract branch name from event
            branch_names = self._extract_branch_names_from_event(event)
            branch_name = branch_names["source_branch"]
            if branch_name:
                # Build URL from event
                url_to_search = self._build_branch_url(event=event, branch_name=branch_name)

        # Search by URL only (no fallback on name - too imprecise)
        if url_to_search:
            return self.env["git.branch"].sudo().search([
                ("url", "=", url_to_search)
            ], limit=1)

        return self.env["git.branch"]

    @api.model
    def _create_or_update_pull_request(self, event, values=None, update_existing=True):
        """
        Create or update a git.pull.request from a webhook event.

        :param event: The webhook event dict
        :param values: Optional dict with additional values to merge (e.g. task_id)
        :param bool update_existing: update existing pull request if found
        :return: git.pull.request record
        """
        values_by_arg = values or {}

        # Prepare default values (task_id passed via values_by_arg)
        create_or_upd_vals = self._prepare_pull_request_vals(event, values=values_by_arg)

        # Extract task for checks and linking
        task_id = create_or_upd_vals.get("task_id")
        task = self.env["project.task"].sudo().browse(task_id) if task_id else self.env["project.task"]

        # Search existing
        existing_pr = self._search_existing_pull_request(event=event)

        # Update if exists
        if existing_pr and update_existing:
            existing_pr.sudo().write(create_or_upd_vals)

        # Create if not exists
        if not existing_pr:
            if not task:
                create_without_task = str2bool(
                    self.env["ir.config_parameter"].sudo().get_param(
                        "webhook_gitlab.option_create_without_task_match",
                        default="True"
                    )
                )
                if not create_without_task:
                    # Don't create pull request without task association
                    return self.env["git.pull.request"]
            new_pr = self.env["git.pull.request"].sudo().create(create_or_upd_vals)

        git_pull_request = existing_pr or new_pr
        if task and git_pull_request.id not in task.git_pull_request_ids.ids:
            # Link to task
            task.write({"git_pull_request_ids": [(4, git_pull_request.id)]})

        return git_pull_request

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
