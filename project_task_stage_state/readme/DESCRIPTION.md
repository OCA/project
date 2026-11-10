This module associates a state to a stage, so that when the stage of
a task is changed, the state is also changed.

When a closing state (done or canceled) is set on a stage, the open tasks
that are already in that stage are closed with that state.
