This module connects the Odoo `project` app with git hosting platforms.

It listens to webhooks (pushes, merge/pull requests, branch
creation/deletion, CI pipelines), records the involved git entities
(commits, branches, pull requests) and links them to the referenced
project tasks, following the Jira-style referencing rules: each entity
is linked to a task only by its own explicit reference (commit message,
branch name, PR/MR title).

This is the base module: install one bridge module per platform to
actually connect it (`project_github`, `project_gitlab`). Without a
bridge the base module does nothing on its own and requires no git
Python library.

Main features:

- track commits, branches and pull/merge requests as Odoo records,
  browsable from the **Project > Git** menu and from the related tasks

- match tasks by explicit database id (`taskid#123` / `tid#123`) or by
  a Jira-style issue-key pattern (e.g. `ABC-123`).

  The id matches anywhere (commit message, branch name, PR/MR title);
  the key is searched in the task names

- post a message on the pull/merge request with a link to the related
  task(s)

- tag the related tasks with the pull/merge request status and the CI
  pipeline status
