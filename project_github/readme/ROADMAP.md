- The CI status of a pull request (`ci_status` field and the `CI: ...`
  task tags) is never populated on GitHub: unlike the GitLab bridge,
  which tracks pipeline events, no CI event handler is implemented
  yet. GitHub reports CI through several webhook families
  (`check_suite`/`check_run` for GitHub Actions and Checks API apps,
  `status` for legacy commit statuses): the natural candidate is a
  `check_suite` handler mapping status/conclusion to `ci_status`,
  with the webhook deployed by the project form subscribing the extra
  event.
