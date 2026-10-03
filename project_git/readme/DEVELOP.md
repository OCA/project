## Writing a platform bridge

A bridge module (see `project_github` / `project_gitlab` as references)
connects one git hosting platform to this base. It provides:

1. **A controller child** extending `ProjectGitWebhook`:

   - `_detect_event_source(headers)`: claim the requests of your
     platform by their specific header, falling through to `super()`
     otherwise. Every bridge claims only what is unmistakably its own,
     so the chain order between bridges never matters. The GitHub
     bridge, for example:

     ```python
     def _detect_event_source(self, headers):
         if headers.get("X-Hub-Signature-256"):
             return "github"
         return super()._detect_event_source(headers)
     ```

   - `_verify_webhook_token_<source>(token)`: authorize the request the
     way your platform does (verbatim token header, payload
     signature, ...).

   - `_parse_git_request_data_<source>(event, headers)`: normalize the
     payload.
     The parser must set the common keys `source`, `repository_url` and
     `project_git_event_type` (mapped from the authoritative event
     discriminator of your platform; `push` events are then refined by
     the base into `branch_creation`/`branch_deletion`/`commit_push`
     via the git-native null-SHA schema).

2. **Model extensions on `project.git.event`** with the per-source
   naming convention `<method>_<source>`.

   Git platforms deliver similar payloads, so the whole connector flow
   (task matching, entity tracking and correlation, messaging) is
   already implemented by the sourceless `_process_*_event` helpers of
   the base (pull request, commit push, branch creation/deletion). The
   helpers cover the residual per-platform differences by dispatching
   hooks by source. A bridge provides:

   - the `_process_<event type>_<source>` entrypoints invoked by the
     controller dispatch: one explicit binding for every event your
     platform handles (an event with no binding for its source is
     skipped silently). Delegating to a `_process_*_event` helper is a
     one-liner:

     ```python
     @api.model
     def _process_pull_request_github(self, event):
         return self._process_pull_request_event(event)
     ```

     For an event the base has no helper for (e.g. a pipeline event,
     which only exists on some platforms) the entrypoint implements the
     whole logic itself.

   - the hooks required by the helpers you delegate to
     (`_dispatch_by_source` warns when one is missing):
     `_extract_pr_title_from_event_<source>`,
     `_extract_branch_names_from_event_<source>`,
     `_build_source_branch_url_<source>`, `_fetch_pr_commits_<source>`,
     `_prepare_pull_request_vals_<source>`,
     `_extract_pr_identifiers_<source>`. Each one maps a platform
     detail onto the shared flow, e.g.:

     ```python
     def _extract_pr_title_from_event_github(self, event):
         return event.get("pull_request", {}).get("title", "")
     ```

   - the optional hooks (silently skipped when missing):
     `_prepare_commit_vals_<source>` (per-platform name/description),
     `_extract_pr_fallback_commits_<source>` (implement only if your
     payload carries honest head-commit data).

   **Normalized commit format**: every commit dict crossing the
   pipeline (webhook payload or API conversion) carries `id` (full
   sha), `message`, `url`, `timestamp`. A platform whose payload
   diverges maps it at the boundary (parser or API converter of the
   bridge), never by reimplementing the generic methods.

3. **The platform API client** on `project.git.auth`
   (`_connect_<source>`), together with the Python library dependency,
   and the per-source hooks of `project.git.pull.request`
   (`_post_message_<source>`, `_is_pr_opening_<source>`,
   `_assign_tags_to_task_<source>`) plus a `selection_add` on its
   `source` field.

   **Task tags**: the bridge owns its whole tagging process — it ships
   its own `project.tags` master-data for the states it populates and
   its `_assign_tags_to_task_<source>` manages only its own tag
   namespace (wipe and re-add via the generic `_replace_task_tags`
   helper). Tag names must be platform-specific (e.g. `PR:` vs `MR:`
   prefixes): `project.tags` names are unique database-wide, and the
   tags of the other platforms must survive your alignment.

4. Optionally, a `_create_project_webhook_<source>` implementation on
   `project.project` (automatic webhook deployment) claiming its URLs
   in `_get_url_platform` with the same claim-or-`super()` pattern as
   above.
