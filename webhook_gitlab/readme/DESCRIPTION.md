This module connects the Odoo `project` app with GitHub and GitLab.

It listens to webhooks (pushes, merge/pull requests, branch
creation/deletion, GitLab pipelines), records the involved git entities
(commits, branches, pull requests) and links them to the referenced
project tasks, following the referencing conventions popularized by
Jira: each entity is linked to a task only by its own explicit
reference (commit message, branch name, PR/MR title).

Main features:

- track commits, branches and pull/merge requests as Odoo records,
  browsable from the **Project > Git** menu and from the related tasks
- match tasks by explicit database id (`taskid#123` / `tid#123`) on any
  surface, or by a configurable issue-key pattern (e.g. `ABC-123`)
  searched in the task names
- post a message on the merged pull/merge request with a link to the
  related task(s)
- tag the related tasks with the pull/merge request status and the CI
  pipeline status (GitLab)
