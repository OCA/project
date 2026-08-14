## Writing a platform bridge

A bridge module (see `project_github` / `project_gitlab` as references)
connects one git hosting platform to this base. It provides:

1. **A controller child** extending `ProjectGitWebhook`:

   - `_detect_event_source(headers)`: claim the requests of your
     platform by their specific header and return your source name;
     fall through to `super()` otherwise. Chain rule: a *specific*
     claim comes **before** `super()`, a *catch-all* claim (accepting
     e.g. any self-hosted instance) comes **after** it, so the MRO
     order between bridges never matters.
   - `_verify_webhook_token_<source>(token)`: authorize the request the
     way your platform does (verbatim token header, payload
     signature, ...).
   - `_parse_request_<source>(event, headers)`: normalize the payload.
     The parser must set the common keys `source`, `repository_url` and
     `project_git_event_type` (mapped from the authoritative event
     discriminator of your platform; `push` events are then refined by
     the base into `branch_creation`/`branch_deletion`/`commit_push`
     via the git-native null-SHA schema).

2. **Model extensions on `project.git.event`** with the per-source
   naming convention `<method>_<source>`:

   - mandatory dispatched implementations (`_dispatch_by_source` warns
     when missing): `_extract_pr_title_from_event_<source>`,
     `_extract_branch_names_from_event_<source>`,
     `_build_source_branch_url_<source>`, `_fetch_pr_commits_<source>`,
     `_prepare_pull_request_vals_<source>`,
     `_extract_pr_identifiers_<source>`;
   - optional hooks of generic methods (silently skipped when missing):
     `_prepare_commit_vals_<source>` (per-platform name/description),
     `_extract_pr_fallback_commits_<source>` (implement only if your
     payload carries honest head-commit data);
   - the `_process_<event type>` handlers that only exist on your
     platform (e.g. a pipeline event).

   **Normalized commit format**: every commit dict crossing the
   pipeline (webhook payload or API conversion) carries `id` (full
   sha), `message`, `url`, `timestamp`. A platform whose payload
   diverges maps it at the boundary (parser or API converter of the
   bridge), never by reimplementing the generic methods.

3. **The platform API client** on `project.git.auth`
   (`_connect_<source>`), together with the Python library dependency,
   and the per-source hooks of `project.git.pull.request`
   (`_post_message_<source>`, `_is_pr_opening_<source>`) plus a
   `selection_add` on its `source` field.

4. Optionally, a `_create_project_webhook_<source>` implementation on
   `project.project` (automatic webhook deployment) claiming its URLs
   in `_get_url_platform` with the same chain rule as above.
