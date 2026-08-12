## Webhook endpoint

Configure your GitHub/GitLab repositories to send webhooks (push,
merge/pull request, pipeline events) to:

    https://<your-odoo-host>/webhook_gitlab/webhook/

In the webhook settings, set a secret token: GitLab sends it in the
`X-Gitlab-Token` header, GitHub signs the payload with it.

## System parameters

- `webhook_gitlab.authorization_token`: the secret token set on the
  webhooks. Incoming requests are rejected when this parameter is
  missing or still set to the demo default.
- `webhook_gitlab.github_token`: GitHub personal access token, used by
  Odoo to call the GitHub API (fetch PR commits, post messages on the
  PR).
- `webhook_gitlab.gitlab_token.<instance-url>/`: GitLab access token,
  one parameter per GitLab instance. The key is the instance root URL
  **with a trailing slash**, e.g.
  `webhook_gitlab.gitlab_token.https://gitlab.com/`.
- `webhook_gitlab.task_name_match_regex`: regex used to extract issue
  keys from commit messages, branch names and PR/MR titles. Seeded on
  install/update with the Jira-strict default `\b[A-Z][A-Z]+-\d+\b`
  and never overwritten once present. Extraction is case-sensitive;
  prepend `(?i)` to relax it. The extracted key is searched
  case-insensitively in the task names.

## Project mapping

To restrict the pattern-based matching to the tasks of a given project,
set the repository URL in the **Git Project URL** field of the project.
Explicit `taskid#`/`tid#` references resolve globally and need no
mapping.
