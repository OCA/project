This module automatically assigns default users to tasks.
- Stage-based assignment (priority rule): When creating a task or changing its stage to one with default users, those users are automatically assigned according to the stage’s assignment mode (replace or merge). Stage-based defaults always take priority over project defaults.
- Project-based fallback: If the stage does not define any default users, project default users are applied using the same assignment mode logic (replace or merge).
- Assignment behavior: The assignment mode controls how users are applied:
  - replace: replaces existing task users with default users
  - merge: adds default users to the existing task users without removing them
- Multiple default users supported: Both project and stage can define multiple default users.
