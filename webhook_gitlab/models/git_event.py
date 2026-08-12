# Copyright 2020, Jarsa
# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re
import logging
import time

from urllib.parse import urljoin

import gitlab  # pylint: disable=W7935
from github import Github

from odoo import api, models

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
    def _process_merge_request(self, event):
        """Process a GitLab Merge Request event."""
        return self._process_pull_request_event(event)

    @api.model
    def _process_pull_request(self, event):
        """Process a GitHub Pull Request event."""
        return self._process_pull_request_event(event)

    @api.model
    def _process_pull_request_event(self, event):
        """Common processing for GitLab MR and GitHub PR events.

        Tasks are matched following the Jira referencing conventions
        (each entity is linked by its own explicit reference only):
        - the PR/MR is linked to the tasks matched (task_match_regex) by
          its title, by its source branch name or by the message of any
          of its commits, restricted to the projects related to the
          repository URL — plus the legacy explicit reference in the
          title (e.g. "task#123"), treated as a title match;
        - the source branch is linked to the same tasks as the PR/MR
          (Jira: a branch is linked when it is the source branch of a
          linked PR/MR);
        - each commit is linked only to the tasks its own message
          mentions.

        The PR/MR and its source branch are single entities per event, so
        they are created/updated once. If no task matches and the PR/MR
        is not already tracked, nothing is created. Finally, every newly
        linked task is notified once with a message on the PR/MR, and
        broken/missing references are warned about (only on PR opening or
        title change, to avoid spamming on every update event).

        :return: the git.pull.request record (empty recordset if the
                 PR/MR is not tracked in Odoo)
        """
        pr_title = self._extract_pr_title_from_event(event)
        matching_tasks = self.env["project.task"].sudo()
        commit_matches = []  # (commit, matching tasks) pairs

        repository_projects = self._get_related_projects_by_url(event=event)
        if repository_projects:
            source_branch = self._extract_branch_names_from_event(event)["source_branch"]
            matching_tasks |= self._find_matching_tasks(projects=repository_projects, pattern_text=source_branch)
            matching_tasks |= self._find_matching_tasks(projects=repository_projects, pattern_text=pr_title)
            # Fetch all PR/MR commits via API (their messages are a
            # matching source), falling back to the head commit carried
            # by the event payload if the call fails
            commits = self._fetch_pr_commits(event) or self._extract_pr_fallback_commits(event)
            for commit in commits:
                commit_matching_tasks = self._find_matching_tasks(projects=repository_projects, pattern_text=commit.get("message", ""))
                if commit_matching_tasks:
                    commit_matches.append((commit, commit_matching_tasks))
                    matching_tasks |= commit_matching_tasks

        # Legacy flow: explicit "task#<id>" reference in the title
        id_found = self._get_record_type_and_id(pr_title)
        if id_found:
            matching_tasks |= self.env["project.task"].sudo().browse(int(id_found["id"])).exists()

        git_pull_request = self._create_or_update_pull_request(event=event, tasks=matching_tasks)

        if git_pull_request:
            git_branch = self._create_or_update_branch(event=event, tasks=matching_tasks)
            # Each commit is linked to the tasks its own message mentions
            tracked_commits = self.env["git.commit"].sudo()
            for commit, commit_matching_tasks in commit_matches:
                tracked_commits |= self._create_or_update_commit(commit=commit, event=event, tasks=commit_matching_tasks)
            # Correlate the tracked entities with each other
            git_pull_request.git_commit_ids |= tracked_commits
            if git_branch:
                git_pull_request.source_branch_id = git_branch
                git_branch.git_commit_ids |= tracked_commits
            git_pull_request._post_task_link_messages(event)

        self.env["git.pull.request"]._post_negative_match_messages(
            event,
            matching_tasks=matching_tasks,
            id_found=id_found,
            repository_projects=repository_projects,
        )
        return git_pull_request

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
    def _extract_pr_title_from_event(self, event):
        """Extract the PR/MR title from the event based on event source.

        :param dict event: The webhook event
        :return: title string (empty string if not present)
        """
        event_source = event.get("source", "gitlab")
        if event_source == "gitlab":
            return event.get("object_attributes", {}).get("title", "")
        return event.get("pull_request", {}).get("title", "")

    @api.model
    def _extract_pr_fallback_commits(self, event):
        """Extract the PR/MR head commit carried by the event payload itself.

        Used as fallback when the full commit list cannot be fetched via API.

        :param dict event: The webhook event
        :return: list with a single commit dict in webhook format (empty
                 list if the event carries no head commit)
        """
        event_source = event.get("source", "gitlab")
        if event_source == "gitlab":
            last_commit = event.get("object_attributes", {}).get("last_commit")
            return [last_commit] if last_commit else []
        pr_data = event.get("pull_request", {})
        head_sha = pr_data.get("head", {}).get("sha", "")
        if not head_sha:
            return []
        return [
            {
                "id": head_sha,
                "message": f"HEAD commit from PR: {pr_data.get('title', '')}",
                "url": f"{pr_data.get('html_url', '')}/commits/{head_sha}",
                "timestamp": pr_data.get("updated_at", ""),
            }
        ]

    @api.model
    def _find_matching_tasks(self, projects, pattern_text):
        """
        Find project tasks that match a given pattern in their name.
        Every pattern occurrence in the text is considered, so a text
        mentioning several tasks matches all of them (as in Jira).
        Returns flat project.task recordset.
        """
        matching_tasks = self.env["project.task"]
        if not pattern_text:
            return matching_tasks

        regex = self._get_task_match_regex()
        patterns = {
            pattern_match.group(0).upper()
            for pattern_match in re.finditer(regex, pattern_text, re.IGNORECASE)
        }

        for pattern in patterns:
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
    def _create_or_update_commit(self, commit, event, values=None, tasks=None, update_existing=True):
        """
        Create or update a git.commit from commit data.

        The commit is identified by full_sha (globally unique).

        :param dict commit: commit data with 'id' (full SHA), 'message', 'url', etc.
        :param dict event: The webhook event (used to extract event_source)
        :param dict values: Optional dict with additional values to override/merge
        :param tasks: Optional project.task recordset to link to the commit
        :param bool update_existing: update existing commit if found
        :return: git.commit record (empty recordset if the commit does not
                 exist yet and there is no task to link it to)
        """
        full_sha = commit.get("id", "")
        if not full_sha:
            return self.env["git.commit"]

        tasks = tasks if tasks is not None else self.env["project.task"]

        create_or_upd_vals = self._prepare_commit_vals(
            commit=commit,
            event=event,
            values=values
        )

        # Search existing commit by full_sha (globally unique)
        existing_commit = self._search_existing_commit(commit=commit)

        if existing_commit and update_existing:
            existing_commit.sudo().write(create_or_upd_vals)

        git_commit = existing_commit
        if not git_commit:
            # Entities are tracked only when related to at least one task
            if not tasks:
                return self.env["git.commit"]
            git_commit = self.env["git.commit"].sudo().create(create_or_upd_vals)

        tasks_to_link = tasks - git_commit.task_ids
        if tasks_to_link:
            git_commit.sudo().write({"task_ids": [(4, task.id) for task in tasks_to_link]})

        return git_commit

    @api.model
    def _create_or_update_branch(self, event, values=None, tasks=None, update_existing=True):
        """
        Create or update a git.branch from event.

        :param dict event: The webhook event
        :param dict values: Optional dict with additional values to override/merge
            (can include "name" and "url")
        :param tasks: Optional project.task recordset to link to the branch
        :param bool update_existing: update existing branch if found
        :return: git.branch record (empty recordset if the branch does not
                 exist yet and there is no task to link it to)
        """
        tasks = tasks if tasks is not None else self.env["project.task"]

        create_or_upd_vals = self._prepare_branch_vals(event, values=values)
        if not create_or_upd_vals.get("name"):
            return self.env["git.branch"]

        # Search existing by URL (unique identifier)
        existing_branch = self._search_existing_branch(
            branch_url=create_or_upd_vals.get("url"),
            event=event
        )

        if existing_branch and update_existing:
            existing_branch.sudo().write(create_or_upd_vals)

        git_branch = existing_branch
        if not git_branch:
            # Entities are tracked only when related to at least one task
            if not tasks:
                return self.env["git.branch"]
            git_branch = self.env["git.branch"].sudo().create(create_or_upd_vals)

        tasks_to_link = tasks - git_branch.task_ids
        if tasks_to_link:
            git_branch.sudo().write({"task_ids": [(4, task.id) for task in tasks_to_link]})

        return git_branch

    @api.model
    def _convert_pygithub_commit_to_dict(self, commit):
        """Convert PyGithub Commit object to dict format.

        Normalizes PyGithub commit objects to the same dict structure
        used by webhooks for uniform handling.

        :param commit: PyGithub Commit object
        :return: dict with keys: id, message, url, timestamp, author
        """
        return {
            "id": commit.sha,
            "message": commit.commit.message,
            "url": commit.html_url,
            "timestamp": commit.commit.author.date.isoformat() if commit.commit.author and commit.commit.author.date else "",
            # Extra fields for future use
            "author": {
                "name": commit.commit.author.name if commit.commit.author else "",
                "email": commit.commit.author.email if commit.commit.author else "",
            },
        }

    @api.model
    def _fetch_github_pr_commits(self, event):
        """Fetch all commits from a GitHub PR and return a list(dict)
        containing commits data.

        :param dict event: The webhook event
        :return: list of commit dicts (same format as webhook)
        """
        try:
            github = self._connect_github()

            repo_full_name = event["repository"]["full_name"]  # "owner/repo"
            pr_number = event["number"]

            # Get PR and commits
            github_repo = github.get_repo(repo_full_name)
            pr = github_repo.get_pull(pr_number)

            # Convert PyGithub Commit objects to dicts (same format as webhook)
            commit_list = []
            for commit in pr.get_commits():
                commit_dict = self._convert_pygithub_commit_to_dict(commit)
                commit_list.append(commit_dict)

            return commit_list

        except Exception as e:
            # Log error but don't fail - fallback will handle it
            _logger.warning(f"Failed to fetch GitHub PR commits: {str(e)}")
            return []

    @api.model
    def _fetch_pr_commits(self, event):
        """Unified dispatcher that calls source-specific implementation
        in order to fetch all commits from PR/MR.

        :param dict event: The webhook event
        :return: list of commits (PyGithub objects for GitHub, dicts for GitLab)
        """
        event_source = event.get("source", "gitlab")

        if event_source == "github":
            return self._fetch_github_pr_commits(event)
        elif event_source == "gitlab":
            return self._fetch_gitlab_mr_commits(event)

        _logger.warning(f"Unknown event source for PR commit fetch: {event_source}")
        return []

    @api.model
    def _convert_gitlab_commit_to_dict(self, commit, project=None):
        """Convert python-gitlab ProjectCommit object to dict format.

        Normalizes python-gitlab commit objects to the same dict structure
        used by webhooks for uniform handling.

        If any field is missing and project is provided, fetches full commit
        via API. In the latter case the commit is fetched with a small delay
        to stay within GitLab's rate limits (10 req/sec limit). This should
        avoid event handling failure when, ad example, a PR has 10+ commits.

        :param commit: python-gitlab ProjectCommit object
        :param project: python-gitlab Project object (optional, for full get() if needed)
        :return: dict with keys
        """

        # Use getattr for each field to detect missing data in case of lazy loading
        commit_id = getattr(commit, 'id', None)
        message = getattr(commit, 'message', None)
        title = getattr(commit, 'title', None)
        url = getattr(commit, 'web_url', None)
        timestamp = getattr(commit, 'created_at', None)
        author_name = getattr(commit, 'author_name', None)
        author_email = getattr(commit, 'author_email', None)
        # If any field is missing and project available, fetch full commit
        if any(field is None for field in [commit_id, message, title, url, timestamp, author_name, author_email]) and project:
            _logger.info(f"Lazy-loaded commit missing fields, fetching full commit: {commit_id or 'unknown'}")
            commit = project.commits.get(commit.id)

            # Re-extract all fields from full commit
            commit_id = getattr(commit, 'id', None)
            message = getattr(commit, 'message', None)
            title = getattr(commit, 'title', None)
            url = getattr(commit, 'web_url', None)
            timestamp = getattr(commit, 'created_at', None)
            author_name = getattr(commit, 'author_name', None)
            author_email = getattr(commit, 'author_email', None)

            # Throttle to respect rate gitlab limits (10 req/sec limit)
            time.sleep(0.3)

        return {
            "id": commit_id or "",
            "message": message or "",
            "title": title or "",
            "url": url or "",
            "timestamp": timestamp or "",
            # Extra fields for future use
            "author": {
                "name": author_name or "",
                "email": author_email or "",
            },
        }

    @api.model
    def _fetch_gitlab_mr_commits(self, event):
        """Fetch all commits from a GitLab MR and return a list(dict)
        containing commits data.

        :param dict event: The webhook event
        :return: list of commit dicts (same format as webhook)
        """
        commit_list = []
        try:
            gl = self._connect_gitlab(url=event["project"]["web_url"])

            project_id = event["project"]["id"]
            mr_iid = event["object_attributes"]["iid"]

            # Get MR and commits
            project = gl.projects.get(project_id)
            mr = project.mergerequests.get(mr_iid)

            # Convert commits into webooh event commit format
            for commit in mr.commits():
                commit_dict = self._convert_gitlab_commit_to_dict(commit, project=project)
                commit_list.append(commit_dict)

        except Exception as e:
            # Log error but don't fail - fallback will handle it
            _logger.warning(f"Failed to fetch GitLab MR commits: {str(e)}")
        return commit_list

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
        """Handle branch creation events with granular task matching
        (see _link_push_entities_to_tasks)."""
        branch_name = self._extract_branch_names_from_event(event)["source_branch"]
        if not branch_name:
            return
        self._link_push_entities_to_tasks(projects, event)

    def _process_branch_deletion(self, projects, event):
        """Handle branch deletion events"""
        # Search for existing branch using the standardized helper (searches by URL)
        existing_branch = self._search_existing_branch(event=event)

        if existing_branch:
            # For now we keep the record but we could add a 'deleted' tag or unlink here
            pass

    def _process_commit_push(self, projects, event):
        """Handle regular commit push events with granular task matching
        (see _link_push_entities_to_tasks)."""
        if not event.get("commits"):
            return
        self._link_push_entities_to_tasks(projects, event)

    def _link_push_entities_to_tasks(self, projects, event):
        """Link the branch and commits of a push-type event (commit push,
        branch creation) to the matching tasks, following the Jira
        referencing conventions (each entity is linked by its own
        explicit reference only):

        - the branch is linked to the tasks its name mentions;
        - each commit is linked only to the tasks its own message
          mentions, so a task referenced on a shared branch (e.g.
          "develop") is not polluted with unrelated resources.
        """
        branch_name = self._extract_branch_names_from_event(event)["source_branch"]
        tasks_from_branch = self._find_matching_tasks(projects=projects, pattern_text=branch_name)

        # The branch is a single entity per event: create/update it once
        git_branch = self._create_or_update_branch(event=event, tasks=tasks_from_branch)

        tracked_commits = self.env["git.commit"].sudo()
        for commit in event.get("commits", []):
            commit_tasks = self._find_matching_tasks(projects=projects, pattern_text=commit.get("message", ""))
            if commit_tasks:
                tracked_commits |= self._create_or_update_commit(commit=commit, event=event, tasks=commit_tasks)

        # Correlate the tracked commits with their branch (a pre-existing
        # branch record is enriched even without new name matches)
        if git_branch:
            git_branch.git_commit_ids |= tracked_commits

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
    def _prepare_commit_vals(self, commit, event, values=None):
        """Prepare commit values from commit for ORM write/create.

        Commit param is always a dict (normalized format) regardless of source:
        - Webhook events: already dict
        - GitHub API: converted via _convert_pygithub_commit_to_dict()
        - GitLab API: already dict from python-gitlab

        :param dict commit: Commit dict with 'id', 'message', 'url', 'timestamp', etc.
        :param dict event: The webhook event (used to extract event source)
        :param dict values: Optional dict with values to override/merge (e.g. "task_id")
        :return: dict of commit values ready for create/write
        """
        values_by_arg = values or {}

        # Extract event source from event
        event_source = event.get("source", "gitlab")

        default_vals = {}
        timestamp = self.env["git.commit"].parse_timestamp(commit.get("timestamp", ""))

        if event_source == "gitlab":
            default_vals.update({
                "name": commit.get("title", ""),
                "description": commit.get("message", ""),
                "url": commit.get("url", ""),
                "full_sha": commit.get("id", ""),
                "timestamp": timestamp,
            })
        elif event_source == "github":
            commit_text_lines = commit.get("message", "").split("\n", 1)
            commit_title = commit_text_lines[0][:60]
            commit_description = commit_text_lines[1] if len(commit_text_lines) > 1 else ""
            default_vals.update({
                "name": commit_title,
                "description": commit_description,
                "url": commit.get("url", ""),
                "full_sha": commit.get("id", ""),
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
    def _prepare_gitlab_merge_request_vals(self, event, values=None):
        """Prepare GitLab merge request values from event for ORM write/create.

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
    def _prepare_github_pull_request_vals(self, event, values=None):
        """Prepare GitHub pull request values from event for ORM write/create.

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
            return self._prepare_gitlab_merge_request_vals(event, values=values)
        elif event_source == "github":
            return self._prepare_github_pull_request_vals(event, values=values)
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
    def _search_existing_commit(self, commit):
        """Search for existing commit by full SHA (globally unique).

        :param dict commit: commit data containing 'id' (full SHA)
        :return: existing commit or empty recordset
        """
        full_sha = commit.get("id", "")
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
    def _create_or_update_pull_request(self, event, values=None, tasks=None, update_existing=True):
        """
        Create or update a git.pull.request from a webhook event.

        :param event: The webhook event dict
        :param values: Optional dict with additional values to override/merge
        :param tasks: Optional project.task recordset to link to the pull request
        :param bool update_existing: update existing pull request if found
        :return: git.pull.request record (empty recordset if the pull request
                 does not exist yet and there is no task to link it to)
        """
        tasks = tasks if tasks is not None else self.env["project.task"]

        create_or_upd_vals = self._prepare_pull_request_vals(event, values=values)

        existing_pr = self._search_existing_pull_request(event=event)

        if existing_pr and update_existing:
            existing_pr.sudo().write(create_or_upd_vals)

        git_pull_request = existing_pr
        if not git_pull_request:
            # Entities are tracked only when related to at least one task
            if not tasks:
                return self.env["git.pull.request"]
            git_pull_request = self.env["git.pull.request"].sudo().create(create_or_upd_vals)

        tasks_to_link = tasks - git_pull_request.task_ids
        if tasks_to_link:
            git_pull_request.sudo().write({"task_ids": [(4, task.id) for task in tasks_to_link]})

        return git_pull_request

    @api.model
    def _connect_gitlab(self, url):
        """Connect to the gitlab instance hosting the given project URL
        and return the gitlab client object.

        :param str url: a project-level URL (e.g. project web_url); the
            instance root is derived from it, and selects the per-instance
            token sysparam (webhook_gitlab.gitlab_token.<instance root>)
        """
        url = urljoin(url, "../..")
        token = self.env["ir.config_parameter"].sudo().get_param("webhook_gitlab.gitlab_token." + url)
        return gitlab.Gitlab(url, private_token=token)

    @api.model
    def _connect_github(self):
        """Connect to github instance and return github object"""
        token = self.env["ir.config_parameter"].sudo().get_param("webhook_gitlab.github_token")
        return Github(token)

