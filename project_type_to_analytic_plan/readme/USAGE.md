Once the root analytic plan is configured, synchronization is automatic:

- Creating a project type creates the corresponding analytic plan.
- Renaming a project type renames the related analytic plan.
- Moving a project type in the hierarchy moves the related analytic plan.
- Deleting a project type deletes the related analytic plan (only if no
  projects nor analytic accounts depend on it).
- Assigning a project type to a project links the project's analytic
  account to the matching analytic plan.

Plans and analytic accounts under the configured root plan are protected
from manual modification or deletion: use the project type tree to make
changes.

To rebuild the entire tree (for instance after a data import), create a
new root analytic plan, select it in the settings, and click
*Synchronize Project Types with Analytic Plans* again. The
synchronization cannot be re-run on the same root plan once analytic
accounts exist below it, due to foreign key constraints; the previous
root plan can be archived or kept for historical reference.

The module relies on two context flags to bypass the read-only
constraints during synchronization: `from_project_type_sync` (plan
modifications triggered by project type changes) and `from_project_sync`
(account `plan_id` modifications triggered by project changes).
