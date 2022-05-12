This module adds a field "Devs" in project tasks with two goals:

- Tracking which dev(s) are working on a specific task.
- Restricting "devs" users visibility only to tasks where they are assigned as devs,
  in order to reduce for them the noise of non-dev tasks on the kanban.
- Subtasks inherit "Devs" values from their parent tasks
- A control is in place when setting an activity to a user with "only devs tasks" enabled in a task that doesn't have that user set as "dev".
