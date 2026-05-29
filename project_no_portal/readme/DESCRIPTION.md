This module add per-company switch block_project_portal_access under Settings > Project.
Active by default.

For a blocking company:

- A constraint forbids privacy_visibility = 'portal' (default becomes employees).
- A post_init_hook migrates existing portal projects. This alone removes portal read access.
- A mixin on project.project/project.task also denies portal users in _search/_check_access.
  This adds an additional security without deleting existing ir.model.access
- The "Share Project" / "Share Task" actions are unbound.
  Calling them, for example from the code, raises an error.
  An uninstall_hook restores them.

Scoped per company (multi-company friendly) and fully reversible.