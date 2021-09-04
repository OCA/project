You can access via timesheets:

#. Go to *Timesheets > Timesheet > All Timesheets*.
#. Create a new record.
#. You will see now that the *Date* field contains also time information.
#. If you don't select any "project", you will be able to select any "task",
   opened or not.
#. Selecting a "task", the corresponding "project" is filled.
#. Selecting a "project", tasks are filtered for only allow
   to select opened tasks for that project. Remember that an opened task is
   a task whose stage doesn't have "Closed" mark checked.
#. At the end of the line, you will see a stop button.
#. When you press this button, the difference between *Date* field and the
   current time is saved in the "Duration" field.
#. You can modify the *Date* field for altering the computation of the
   duration.
#. After a record is stopped, you see a *Resume* button, which will open a
   wizard that inherits all relevant values from that timesheet line and lets
   you duplicate it to indicate you start working in the same thing.
#. If you didn't stop the timer, but still hit *Resume* in any other, the
   wizard will tell you that you have a running timer and that starting a new
   one will stop the other one that is running.

To access the wizard directly:

#. Go to *Timesheet > Timesheet > Start work*.
#. You will be able to enter a new timesheet line from scratch, but by using
   this wizard, you avoid problems with old or duplicate running timers.

Or via projects:

#. Go to *Project > Projects*.
#. If a project has a running timesheet line, it will display a *Stop* button.
#. Other projects that have enabled timesheets will display a *Start* button
   that will open the same wizard as the timesheet lines, but duplicating
   project's last timesheet line without a task.
#. You can see the same in list and form views.

Or via tasks:

#. Go to *Project > All Tasks*.
#. If a task has a running timesheet line, it will display a *Stop* button.
#. Other tasks that have enabled timesheets will display a *Start* button
   that will open the same wizard as the timesheet lines, duplicating task's
   last timesheet line.
#. You can see the same in list view.
#. Click on any existing task or create a new one.
#. You can see the same feature in the action buttons box.
#. On the *Timesheets* page, you will be able to handle records the same way
   as you do in the above explanation (except the task selection part, which
   in this case doesn't appear as it's the current one).

Note: All the *Start/Resume/Stop* features are disabled if you don't belong to
the *Timesheets/User* group or if you are viewing a timesheet that belongs
to another user.
