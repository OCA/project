This module extends functionality of the project_task_pull_request module. It adds a
"State" field to Task alongside with PR URI field.

Following pre-defined states are available: "Draft", "Open", "Merged", "Closed". You can
add or modify this list easily by overriding the "selection_pr_state" function in the
"project.task" model
