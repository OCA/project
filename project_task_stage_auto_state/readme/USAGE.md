To use this module, you need to:

1. Enter debug mode
1. Go to Project > Configuration > Task Stages
1. Select or create a stage
1. Configure the automatic actions:
   - Set "Auto-mark as done after days" to the desired number of days (0 to disable)
   - Activate shown boolean fields for states that you want to do something
   - Set "Auto-cancel after days" to the desired number of days (0 to disable)
   - Activate shown boolean fields for states that you want to do something
1. Verify that the scheduled action "Project: Auto-change task state by stage" is
   active in Settings > Technical > Automation > Scheduled Actions
1. When a task is auto-changed, a message is posted in the chatter indicating the
   automatic action

**Notes**:
- The counter starts from the "Last Stage Update" date, which is updated each time a task changes stage
- If both auto-done and auto-cancel are configured for the same stage and both thresholds are reached, auto-done takes precedence
