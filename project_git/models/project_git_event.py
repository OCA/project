# Copyright 2020, Jarsa
# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging
import re

from odoo import api, models
from odoo.osv import expression

_logger = logging.getLogger(__name__)


class ProjectGitEvent(models.Model):
    _name = "project.git.event"
    _description = "Git Webhook Event Processor"

    @api.model
    def _dispatch_by_source(self, event, method_name, *args, mandatory=True, **kwargs):
        """Route a call to the platform-specific implementation
        (<method_name>_<source>) based on event["source"].

        With mandatory=True a missing implementation is warned about
        (dispatched methods); with mandatory=False it is silently
        skipped (optional per-source hooks of generic methods).
        """
        source = event.get("source")
        if hasattr(self, f"{method_name}_{source}"):
            return getattr(self, f"{method_name}_{source}")(event, *args, **kwargs)
        if mandatory:
            _logger.warning("No %s implementation for source %r", method_name, source)
        return None

    @api.model
    def _process_pull_request_event(self, event):
        """Common processing for pull/merge request events, shared by
        the per-source _process_* handlers of the platform bridges.

        Every entity is linked to a task by its own explicit reference:
        an issue key pattern (searched in the names of the tasks
        of the projects related to the repository URL) or an explicit
        "taskid#<id>"/"tid#<id>" reference (resolved globally by id,
        no repository mapping needed). Case by case:

        - the PR/MR is linked to a task when the task is referenced in
          its title, in its source branch name, or in the message of
          any of its commits;
        - the source branch is linked to the same tasks as the PR/MR
          (a branch is linked when it is the source branch of a linked
          PR/MR);
        - a commit is linked to a task only when its own message
          references it; the other PR/MR commits are not tracked.

            task reference found in | PR/MR | branch | commit
            ------------------------+-------+--------+-------
            PR/MR title             |   X   |   X    |
            source branch name      |   X   |   X    |
            PR/MR commit message    |   X   |   X    |   X

            ("commit" means the referencing commit only)

        The PR/MR and its source branch are single entities per event, so
        they are created/updated once. If no task matches and the PR/MR
        is not already tracked, nothing is created. Finally, every newly
        linked task is notified once with a message on the PR/MR, and
        broken/missing references are warned about (only on PR opening or
        title change, to avoid spamming on every update event).

        :return: the project.git.pull.request record (empty recordset if
                 the PR/MR is not tracked in Odoo)
        """
        pr_title = self._extract_pr_title_from_event(event)
        source_branch = self._extract_branch_names_from_event(event)["source_branch"]
        matching_tasks = self.env["project.task"].sudo()
        commit_matches = []  # (commit, matching tasks) pairs

        repository_projects = self._get_related_projects_by_url(event=event)
        matching_tasks |= self._find_matching_tasks(
            projects=repository_projects, pattern_text=source_branch
        )
        matching_tasks |= self._find_matching_tasks(
            projects=repository_projects, pattern_text=pr_title
        )
        # Fetch all PR/MR commits via API (their messages are a
        # matching source), falling back to the head commit carried
        # by the event payload if the call fails
        commits = self._fetch_pr_commits(event) or self._extract_pr_fallback_commits(
            event
        )
        for commit in commits:
            commit_matching_tasks = self._find_matching_tasks(
                projects=repository_projects, pattern_text=commit.get("message", "")
            )
            if commit_matching_tasks:
                commit_matches.append((commit, commit_matching_tasks))
                matching_tasks |= commit_matching_tasks

        git_pull_request = self._get_or_create_pull_request(
            event=event, tasks=matching_tasks
        )

        if git_pull_request:
            git_branch = self._get_or_create_branch(event=event, tasks=matching_tasks)
            # Each commit is linked to the tasks its own message mentions
            tracked_commits = self.env["project.git.commit"].sudo()
            for commit, commit_matching_tasks in commit_matches:
                tracked_commits |= self._get_or_create_commit(
                    commit=commit, event=event, tasks=commit_matching_tasks
                )
            # Correlate the tracked entities with each other
            git_pull_request.git_commit_ids |= tracked_commits
            if git_branch:
                git_pull_request.source_branch_id = git_branch
                git_branch.git_commit_ids |= tracked_commits
            git_pull_request._post_task_link_messages(event)

        self.env["project.git.pull.request"]._post_negative_match_messages(
            event,
            matching_tasks=matching_tasks,
            title_task_references=self.env[
                "project.git.utils"
            ]._extract_task_id_references(pr_title),
            repository_projects=repository_projects,
        )
        return git_pull_request

    @api.model
    def _extract_branch_names_from_event(self, event):
        """Extract source and target branch names from the event.

        Returns dict with:
        - source_branch: The branch where changes come from (or the only
          branch for push events)
        - target_branch: The branch where changes go to (only for MR/PR
          events, empty string otherwise)

        :param dict event: The webhook event
        :return: dict with 'source_branch' and 'target_branch' keys
            (empty strings if not present)
        """
        return self._dispatch_by_source(event, "_extract_branch_names_from_event") or {
            "source_branch": "",
            "target_branch": "",
        }

    @api.model
    def _extract_branch_names_from_ref(self, event):
        """Extract the branch names of a push-type event (branch
        creation/deletion, commit push) from its ref field.

        The 'refs/heads/<branch>' layout is git's own ref schema, not a
        platform convention: platforms usually carry it verbatim in
        their push payloads, so the per-source implementations can
        share this extraction.
        """
        # Extract branch name from ref (e.g., 'refs/heads/feature' -> 'feature')
        ref = event.get("ref", "")
        if ref and ref.startswith("refs/heads/"):
            branch_name = ref.replace("refs/heads/", "")
        else:
            branch_name = ref
        # No target_branch for push events
        return {
            "source_branch": branch_name,
            "target_branch": "",
        }

    @api.model
    def _extract_pr_title_from_event(self, event):
        """Extract the PR/MR title from the event based on event source.

        :param dict event: The webhook event
        :return: title string (empty string if not present)
        """
        return self._dispatch_by_source(event, "_extract_pr_title_from_event") or ""

    @api.model
    def _extract_pr_fallback_commits(self, event):
        """Extract the PR/MR head commit carried by the event payload itself.

        Used as fallback when the full commit list cannot be fetched
        via API (e.g. missing platform token). The per-source
        implementation is an optional hook: platforms whose payload
        carries no honest head-commit data (e.g. only a head sha)
        simply do not implement it, and their PR commit tracking
        relies on the API fetch alone.

        :param dict event: The webhook event
        :return: list with a single commit dict in webhook format (empty
                 list if the event carries no head commit)
        """
        return (
            self._dispatch_by_source(
                event, "_extract_pr_fallback_commits", mandatory=False
            )
            or []
        )

    @api.model
    def _find_matching_tasks(self, projects, pattern_text):
        """
        Find the project tasks referenced by a given text (PR/MR title,
        branch name, commit message). Two always-active mechanisms, with
        every occurrence considered (a text referencing several tasks
        matches all of them):

        - explicit task id reference ("taskid#123" or "tid#123"):
          resolved globally by database id, regardless of the given
          projects (an explicit id needs no repository mapping);
          references to non-existent tasks are silently skipped;

        - issue key pattern: every extracted occurrence is searched in
          the names of the tasks of the given projects (the projects
          related to the repository URL), whatever the task state: a
          reference to a closed task still links the git activity.

        The key extraction is case-sensitive (avoids false positives
        such as "utf-8"); the extracted key is then searched in the
        task names case-insensitively, as a task naming tolerance.
        Returns flat project.task recordset.
        """
        # sudo: the flow runs with the user who enqueued the webhook job
        # (the public user), which has no access to tasks on its own
        matching_tasks = self.env["project.task"].sudo()
        if not pattern_text:
            return matching_tasks

        # Explicit id references: global, not restricted to the projects
        # (a reference to a non-existent task resolves to an empty set)
        for task_id in self.env["project.git.utils"]._extract_task_id_references(
            pattern_text
        ):
            matching_tasks |= self.env["project.task"].sudo().browse(task_id).exists()

        regex = self.env["project.git.utils"]._get_task_name_match_regex()
        patterns = {
            pattern_match.group(0) for pattern_match in re.finditer(regex, pattern_text)
        }

        if not (patterns and projects):
            return matching_tasks

        # DB-side prefilter: candidate tasks whose name contains any
        # key, substring case-insensitive (the extracted keys carry no
        # LIKE wildcard). A whole-word match is always a substring
        # match, so no true match can be lost here.
        ilike_domains = [[("name", "ilike", pattern)] for pattern in patterns]
        candidate_tasks = (
            self.env["project.task"]
            .sudo()
            .search(
                expression.AND(
                    [[("project_id", "in", projects.ids)], expression.OR(ilike_domains)]
                )
            )
        )
        # Python refinement on the candidates: the whole-word match
        # (\b) is the one check ilike cannot express. Given the key
        # "AZ-123", the task "az-123 customer request.." is kept,
        # while "XAZ-1234 customer request.." is discarded
        for task in candidate_tasks:
            if any(
                re.search(rf"\b{re.escape(pattern)}\b", task.name, re.IGNORECASE)
                for pattern in patterns
            ):
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

        repository_projects = (
            self.env["project.project"]
            .sudo()
            .search(
                [
                    "|",
                    ("git_project_url", "in", urls_to_check),
                    ("git_dev_project_url", "in", urls_to_check),
                ]
            )
        )

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
        return self._dispatch_by_source(event, "_build_branch_url", branch_name) or ""

    @api.model
    def _get_or_create_commit(
        self, commit, event, values=None, tasks=None, update_existing=True
    ):
        """
        Get or create a project.git.commit from commit data, linking it
        to tasks.

        The commit is identified by full_sha (globally unique); an existing
        record is refreshed with the event data unless update_existing=False.

        :param dict commit: commit data with 'id' (full SHA), 'message', 'url', etc.
        :param dict event: The webhook event (used to extract event_source)
        :param dict values: Optional dict with additional values to override/merge
        :param tasks: Optional project.task recordset to link to the commit
        :param bool update_existing: update existing commit if found
        :return: project.git.commit record (empty recordset if the commit
                 does not exist yet and there is no task to link it to)
        """
        full_sha = commit.get("id", "")
        if not full_sha:
            return self.env["project.git.commit"]

        tasks = tasks if tasks is not None else self.env["project.task"]

        create_or_upd_vals = self._prepare_commit_vals(
            event=event, commit=commit, values=values
        )

        # Search existing commit by full_sha (globally unique)
        existing_commit = self._search_existing_commit(commit=commit)

        if existing_commit and update_existing:
            existing_commit.sudo().write(create_or_upd_vals)

        git_commit = existing_commit
        if not git_commit:
            # Entities are tracked only when related to at least one task
            if not tasks:
                return self.env["project.git.commit"]
            git_commit = (
                self.env["project.git.commit"].sudo().create(create_or_upd_vals)
            )

        tasks_to_link = tasks - git_commit.task_ids
        if tasks_to_link:
            git_commit.sudo().write(
                {"task_ids": [(4, task.id) for task in tasks_to_link]}
            )

        return git_commit

    @api.model
    def _get_or_create_branch(
        self, event, values=None, tasks=None, update_existing=True
    ):
        """
        Get or create a project.git.branch from event, linking it to tasks.

        The branch is identified by URL; an existing record is refreshed
        with the event data unless update_existing=False.

        :param dict event: The webhook event
        :param dict values: Optional dict with additional values to override/merge
            (can include "name" and "url")
        :param tasks: Optional project.task recordset to link to the branch
        :param bool update_existing: update existing branch if found
        :return: project.git.branch record (empty recordset if the branch
                 does not exist yet and there is no task to link it to)
        """
        tasks = tasks if tasks is not None else self.env["project.task"]

        create_or_upd_vals = self._prepare_branch_vals(event, values=values)
        if not create_or_upd_vals.get("name"):
            return self.env["project.git.branch"]

        # Search existing by URL (unique identifier)
        existing_branch = self._search_existing_branch(
            branch_url=create_or_upd_vals.get("url"), event=event
        )

        if existing_branch and update_existing:
            existing_branch.sudo().write(create_or_upd_vals)

        git_branch = existing_branch
        if not git_branch:
            # Entities are tracked only when related to at least one task
            if not tasks:
                return self.env["project.git.branch"]
            git_branch = (
                self.env["project.git.branch"].sudo().create(create_or_upd_vals)
            )

        tasks_to_link = tasks - git_branch.task_ids
        if tasks_to_link:
            git_branch.sudo().write(
                {"task_ids": [(4, task.id) for task in tasks_to_link]}
            )

        return git_branch

    @api.model
    def _fetch_pr_commits(self, event):
        """Fetch all commits from the PR/MR through the source-specific
        platform API.

        :param dict event: The webhook event
        :return: list of commit dicts (same format as webhook)
        """
        return self._dispatch_by_source(event, "_fetch_pr_commits") or []

    @api.model
    def _process_branch_creation(self, event):
        """Handle branch creation events with granular task matching
        (see _link_push_entities_to_tasks)."""
        branch_name = self._extract_branch_names_from_event(event)["source_branch"]
        if not branch_name:
            return
        repository_projects = self._get_related_projects_by_url(event=event)
        self._link_push_entities_to_tasks(repository_projects, event)

    @api.model
    def _process_branch_deletion(self, event):
        """Handle branch deletion events"""
        # Search for existing branch using the standardized helper (searches by URL)
        existing_branch = self._search_existing_branch(event=event)

        if existing_branch:
            # For now we keep the record but we could add a 'deleted' tag or unlink here
            pass

    @api.model
    def _process_commit_push(self, event):
        """Handle regular commit push events with granular task matching
        (see _link_push_entities_to_tasks)."""
        if not event.get("commits"):
            return
        repository_projects = self._get_related_projects_by_url(event=event)
        self._link_push_entities_to_tasks(repository_projects, event)

    def _link_push_entities_to_tasks(self, projects, event):
        """Link the branch and commits of a push-type event (commit push,
        branch creation) to the matching tasks. Every entity is linked
        by its own explicit reference (an issue key pattern or a
        "taskid#<id>"/"tid#<id>" reference). Case by case:

        - the branch is linked to the tasks referenced in its name.
          The commits it carries are not: untracked commits stay one
          click away through the branch link;
        - a commit is linked to the tasks referenced in its own
          message, and the link stops there: the branch it was pushed
          to (e.g. a shared "develop") and the other commits of the
          push are not linked.

        The repository->project mapping only scopes the pattern
        matching (explicit "taskid#"/"tid#" references work without
        it): events from unmapped repositories are processed too, and
        simply create nothing unless they carry explicit id references.
        """
        branch_name = self._extract_branch_names_from_event(event)["source_branch"]
        tasks_from_branch = self._find_matching_tasks(
            projects=projects, pattern_text=branch_name
        )

        # The branch is a single entity per event: get/create it once
        git_branch = self._get_or_create_branch(event=event, tasks=tasks_from_branch)

        tracked_commits = self.env["project.git.commit"].sudo()
        for commit in event.get("commits", []):
            commit_tasks = self._find_matching_tasks(
                projects=projects, pattern_text=commit.get("message", "")
            )
            if commit_tasks:
                tracked_commits |= self._get_or_create_commit(
                    commit=commit, event=event, tasks=commit_tasks
                )

        # Correlate the tracked commits with their branch (a pre-existing
        # branch record is enriched even without new name matches)
        if git_branch:
            git_branch.git_commit_ids |= tracked_commits

    @api.model
    def _prepare_commit_vals(self, event, commit, values=None):
        """Prepare commit values from commit for ORM write/create.

        The event comes first, as in every dispatched/hook signature.
        Commit param is always a dict (normalized format) regardless of source:
        - Webhook events: already dict
        - Platform APIs: converted by the bridge (e.g.
          _convert_pygithub_commit_to_dict) into the same dict format

        :param dict event: The webhook event (used to extract event source)
        :param dict commit: Commit dict with 'id', 'message', 'url', 'timestamp', etc.
        :param dict values: Optional dict with values to override/merge (e.g. "task_id")
        :return: dict of commit values ready for create/write
        """
        values_by_arg = values or {}

        default_vals = {
            "url": commit.get("url", ""),
            "full_sha": commit.get("id", ""),
            "timestamp": self.env["project.git.commit"].parse_timestamp(
                commit.get("timestamp", "")
            ),
        }
        # name/description come from platform-specific commit fields
        source_vals = self._dispatch_by_source(
            event, "_prepare_commit_vals", commit, mandatory=False
        )
        default_vals.update(source_vals or {})

        # Merge with values_by_arg (task_id, etc.)
        return {**default_vals, **values_by_arg}

    @api.model
    def _prepare_branch_vals(self, event, values=None):
        """Prepare branch values from event.

        Extracts branch name and URL from event using helpers if not provided in values.

        :param dict event: The webhook event
        :param dict values: Optional dict with values to override/merge
            (e.g. "name", "url", "task_id")
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
    def _prepare_pull_request_vals(self, event, values=None):
        """Prepare project.git.pull.request values based on event source.

        :param dict event: The webhook event
        :param dict values: Optional dict with values to override/merge (e.g. "task_id")
        :return: dict of pull request values ready for create/write
        """
        values = values or {}
        return (
            self._dispatch_by_source(event, "_prepare_pull_request_vals", values=values)
            or values
        )

    @api.model
    def _search_existing_pull_request(self, event):
        """Search for existing pr by id_request/id_project (might check by url)
        :param dict event: git event
        :return: existing pull request or empty recordset"""
        pr_identifiers = self._dispatch_by_source(event, "_extract_pr_identifiers")
        if not pr_identifiers:
            return self.env["project.git.pull.request"]
        project_id, request_id = pr_identifiers

        return (
            self.env["project.git.pull.request"]
            .sudo()
            .search(
                [
                    ("id_request", "=", request_id),
                    ("id_project", "=", project_id),
                ],
                limit=1,
            )
        )

    @api.model
    def _search_existing_commit(self, commit):
        """Search for existing commit by full SHA (globally unique).

        :param dict commit: commit data containing 'id' (full SHA)
        :return: existing commit or empty recordset
        """
        full_sha = commit.get("id", "")
        if not full_sha:
            return self.env["project.git.commit"]

        return (
            self.env["project.git.commit"]
            .sudo()
            .search([("full_sha", "=", full_sha)], limit=1)
        )

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
                url_to_search = self._build_branch_url(
                    event=event, branch_name=branch_name
                )

        # Search by URL only (no fallback on name - too imprecise)
        if url_to_search:
            return (
                self.env["project.git.branch"]
                .sudo()
                .search([("url", "=", url_to_search)], limit=1)
            )

        return self.env["project.git.branch"]

    @api.model
    def _get_or_create_pull_request(
        self, event, values=None, tasks=None, update_existing=True
    ):
        """
        Get or create a project.git.pull.request from a webhook event,
        linking it to tasks.

        An existing record is refreshed with the event data unless
        update_existing=False.

        :param event: The webhook event dict
        :param values: Optional dict with additional values to override/merge
        :param tasks: Optional project.task recordset to link to the pull request
        :param bool update_existing: update existing pull request if found
        :return: project.git.pull.request record (empty recordset if the
                 pull request does not exist yet and there is no task to
                 link it to)
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
                return self.env["project.git.pull.request"]
            git_pull_request = (
                self.env["project.git.pull.request"].sudo().create(create_or_upd_vals)
            )

        tasks_to_link = tasks - git_pull_request.task_ids
        if tasks_to_link:
            git_pull_request.sudo().write(
                {"task_ids": [(4, task.id) for task in tasks_to_link]}
            )

        return git_pull_request
