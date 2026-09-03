On each stage (Project → Configuration → Stages):

1. Set the **State** field to the state that moving to this stage should assign.
2. Enable **Sync State → Stage** to also activate the reverse: tasks whose state
   is set to that value will automatically move to this stage.

**Uniqueness rule:** Only one stage per project may have *Sync State → Stage*
enabled for a given state value. Attempting to enable it on a second stage that
shares the same state and project will raise a validation error naming the
conflicting stage. Two  different projects are allowed to each
have their own stage with sync  enabled for the same state — for example,
both "Project A / Done" and "Project B / Done" can independently have
*Sync State → Stage* ticked for the *Done* state. The uniqueness rule only
applies within a single project.
