This module extends functionality of the project_task_pull_request module.
It adds a "State" field to Task alongside with PR URI field.

Default PR state can be defined in Project. When a PR URI is added to a task PR state will be set
based on the task project settings.

Following pre-defined states are available: "Draft", "Open", "Merged", "Closed".
