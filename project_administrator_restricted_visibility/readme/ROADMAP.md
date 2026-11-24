Since 20.0, visibility is limited by two `ir.access` restrictions (records
without a group) whose domain only applies to users in *Restricted
Administrator* but not in *Full Administrator*, using `user.has_groups()`.
Restrictions are combined with every permission, so they also limit the
"see all" permissions that other modules grant to project administrators
(e.g. `hr_timesheet`, `project_todo`). Archiving or overriding the core
permissions would not cover those.

Limitations:

- The restrictions are evaluated for every user. Users outside the
  restricted group get an empty domain, so their queries are unchanged.
- Restricted administrators can only create, edit or delete projects and
  tasks they can see. They can't create a private project managed by
  someone else.
