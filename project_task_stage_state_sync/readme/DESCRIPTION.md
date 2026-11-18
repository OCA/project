This module extends `project_task_stage_state` to complete the bidirectional
link between task states and stages.

`project_task_stage_state` already handles the **Stage → State** direction:
moving a task to a stage updates its state to the one configured on that stage.

This module adds the **State → Stage** direction: when a task's state changes
(manually or programmatically), the task is
automatically moved to the stage configured for that state.

The sync is configured per stage via a checkbox, so it can be enabled selectively
without affecting every stage in every project.
