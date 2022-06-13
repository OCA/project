This module adds a field "Task Team" in project tasks with two goals:

- Tracking which team member(s) are working on a specific task.
- Restricting "Task Team member" users visibility only to tasks where they are assigned as Task team,
  in order to reduce for them the noise of non-task-team member tasks on the kanban.
- Subtasks inherit "Task Team member" values from their parent tasks
- A control is in place when setting an activity to a user with "Visualize only 'Task Team' project tasks" enabled in a task that doesn't have that user set as "Task Team" member.
