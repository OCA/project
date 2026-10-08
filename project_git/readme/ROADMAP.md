- Pipeline tracking is currently GitLab-only; GitHub Actions support
  could be added in the same way (the CI status and tags already live
  in this base module).
- Platform issues are not tracked: the module processes pushes
  (commits and branches), pull/merge requests and CI pipelines only.
  Both platforms deliver issue events on their webhooks, so issue
  tracking could be added in the same way.
- Task references are only evaluated when the platform delivers the
  event: there is no automatic recovery for events missed while Odoo
  was unreachable. Missed deliveries can be resent manually from the
  webhook page of the repository (GitLab keeps the last two days of
  deliveries and disables a webhook after repeated failures — re-enable
  it if Odoo was down for long; on GitHub failed deliveries can also be
  redelivered via API script). Every git entity is created
  idempotently — matched by its sha or platform identifier — so
  redelivering an already-processed event is safe.
