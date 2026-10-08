Link your git activity to a task, step by step:

1. **Map the Odoo project to the repository** (see *Configure*).

   This is the prerequisite for issue-key matching; skip it only if
   you plan to use explicit `taskid#` references exclusively.

2. **Put an issue key in the task name**, e.g. rename the task to
   `ABC-123 fix login`. The key is the handle your git references will
   point to.

   To reference the task by database id instead, skip this step:
   explicit ids need no naming convention.

3. **Mention the reference in your git activity**: write the issue key
   (`ABC-123`), or the explicit id (`taskid#<id>` / `tid#<id>`), in a
   commit message, a branch name or a PR/MR title.

4. **Trigger the event**: push the commits, create the branch, open or
   update the PR/MR.

   The webhook fires and the module records the git entities and links
   them to the referenced tasks.

5. **Check the result on the task**: open the task and follow the
   PR/branch/commit smart buttons, or browse every recorded entity from
   the **Project > Git** menu (**Pull Requests**, **Branches**,
   **Commits**).

When a task is linked to a PR/MR (typically on opening), a message
with the task link is posted on the PR/MR, and the task tags track
the PR/MR and CI pipeline status.

Entities referencing no task are not recorded at all, so unrelated
repositories can safely share the same webhook endpoint.

## How the matching works

A reference written in your git activity (a commit message, a branch
name, a PR/MR title) can point to a task in **two different ways**:

- **By issue key**: you write a Jira-style key (e.g. `ABC-123`) both in
  the task name and in your git activity, and the module matches the
  two.

  This is the everyday way, and it needs the project mapping.

- **By database id**: you write `taskid#<id>` or `tid#<id>` (the id of
  the task in the Odoo database, e.g. `taskid#42`) in your git
  activity.

  This points straight to one task, with no project mapping and no task
  naming convention needed; references to non-existent ids are silently
  ignored.

  Mind the intrinsic limits of database ids before adopting them as
  your everyday convention: a wrong-but-existing id links the wrong
  task with no error to catch it, and ids are not portable across
  databases (the same task carries different ids on staging and
  production).

### Matching by issue key

The referencing conventions mirror the Jira ones (see [Referencing
issues in your development
work](https://confluence.atlassian.com/jirasoftware/referencing-issues-in-your-development-work-1688898766.html)):
if you are used to linking Jira issues from git, you already know how
this works.

An **issue key** is a Jira-style key: two or more uppercase letters, a
dash and a number, such as `ABC-123`. The matching works in two steps:

1. **Key detection, on the git side**: the module scans the text where
   you wrote the reference — the commit message, the branch name, the
   PR/MR title — and picks up every occurrence of the key format
   above, so a text mentioning several keys references all of them.

   The detection is case-sensitive: the key must be written in
   uppercase to be picked up, so `ABC-123 abc-124: fix login` detects
   `ABC-123` only.

2. **Task lookup, on the Odoo side**: each detected key is searched —
   as a whole word, case-insensitively — in the names of the tasks of
   the projects mapped to the repository (see *Project mapping* in
   *Configure*): `ABC-123` links both "ABC-123 fix login" and "Login
   page (abc-123)". Without a mapped project, issue keys match
   nothing.

   The task state does not matter: a reference to a **Done** task
   still links the git activity, since late commits on a closed task
   are common.

### Examples

With a task named `ABC-123 fix login` in a project mapped to the
repository:

- commit message `ABC-123 handle the empty password case` → links the
  commit to the task

- branch named `ABC-123-login-fix` → links the branch to the task

- MR titled `Login fixes for ABC-123` → links the MR (and its source
  branch) to the task

- commit message `abc-123 handle the empty password case` → links
  nothing: the key detection is case-sensitive

With any task, whatever its name, whose database id is 42:

- commit message `taskid#42 handle the empty password case` → links the
  commit to the task

- branch named `tid#42-login-fix` → links the branch to the task

- PR titled `Login fixes for tid#42` → links the PR (and its source
  branch) to the task

### Which entity gets linked

Each entity is linked through its own references only — a commit never
links a task just because it was pushed on a matching branch:

| A key found in…                       | links the commit | the branch             | the PR/MR |
| ------------------------------------- | ---------------- | ---------------------- | --------- |
| a commit message (push event)         | ✓                | —                      | —         |
| the branch name (push event)          | —                | ✓                      | —         |
| a commit message (PR/MR event)        | ✓                | ✓ (only source branch) | ✓         |
| the source branch name (PR/MR event)  | —                | ✓ (only source branch) | ✓         |
| the PR/MR title (PR/MR event)         | —                | ✓ (only source branch) | ✓         |

On PR/MR events the source branch inherits every task linked to the
PR/MR itself.
