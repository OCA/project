- Split the module into a platform-agnostic base plus one extension
  module per platform (GitHub / GitLab), so each deployment only pulls
  the Python library it needs.
- Pipeline tracking is currently GitLab-only; GitHub Actions support
  could be added along the same lines.
- Task references are only evaluated when the platform delivers the
  event: there is no backfill/resync mechanism for events missed while
  Odoo was unreachable.
