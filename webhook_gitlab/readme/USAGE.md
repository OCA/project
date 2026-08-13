Reference a task from your git activity in one of two ways:

- **Issue key pattern**: put the key (e.g. `ABC-123`) in the task
  name, then mention it in a commit message, branch name or PR/MR
  title.
- **Explicit id**: mention `taskid#<id>` or `tid#<id>` (the task
  database id) on any of the same surfaces.

All the linked entities are visible on the task and browsable from the
**Project > Git** menu. When a PR/MR is merged, a message with the task
link is posted on it, and the task tags track the PR/MR and CI pipeline
status. Entities referencing no task are not recorded at all, so
unrelated repositories can safely share the same webhook endpoint.

## How issue keys are matched

The referencing conventions mirror the Jira ones (see [Reference issues
in your development
work](https://support.atlassian.com/jira-software-cloud/docs/reference-issues-in-your-development-work/)):
if you are used to linking Jira issues from git, you already know how
this works.

An **issue key** is a Jira-style key: two or more uppercase letters, a
dash and a number, such as `ABC-123`. The matching works in two steps:

1. **Extraction**: every key occurrence is extracted from the text, so
   a text mentioning several keys references all of them. Extraction is
   case-sensitive: `ABC-123 abc-124: fix login` yields `ABC-123` only.
2. **Task lookup**: each key is searched — as a whole word,
   case-insensitively — in the names of the tasks of the projects
   mapped to the repository (see *Project mapping* in *Configure*):
   `ABC-123` links both "ABC-123 fix login" and "Login page (abc-123)".
   Without a mapped project, pattern keys match nothing. The task state
   does not matter: a reference to a **Done** task still links the git
   activity, since late commits on a closed task are common.

Explicit `taskid#<id>`/`tid#<id>` references skip both steps: they
resolve globally by database id, so they need no project mapping and no
task naming convention. References to non-existent ids are silently
ignored.

Each entity is then linked through its own references only — a commit
never links a task merely because it was pushed on a matching branch:

| A key found in…                    | links the commit | the branch | the PR/MR |
| ---------------------------------- | ---------------- | ---------- | --------- |
| a commit message (push)            | ✓ (that commit)  | —          | —         |
| the branch name (push)             | —                | ✓          | —         |
| a commit message (PR/MR event)     | ✓ (that commit)  | ✓ (source) | ✓         |
| the source branch name (PR/MR)     | —                | ✓ (source) | ✓         |
| the PR/MR title                    | —                | ✓ (source) | ✓         |

On PR/MR events the source branch inherits every task linked to the
PR/MR itself.
