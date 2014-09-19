Employees are now basic Project users, able to create new documents (Issues
or Tasks). These are kept editable while in New and Cancelled states, to
allow for corrections or for the user himself to cancel an incorrectly
created request.
Previously, Employee users did not have any write nor create access to project
documents.

Project Users, on the other hand, are supposed to act on these documents,
such as reported issues, and update them accordingly, so they have write
access for all states. Employee users don't have write access on later states,
but can still write comments and communicate through the message board (open
chatter).

In general, users will only be able to see documents where:

  * They are assigned/responsible for, or
  * They are following, or
  * They are a team member for the corresponding Project (but not if only in
    the project's follower list).


Project Managers have access rules similar to Project Users, but additionally
can create new projects and can see all documents for the projects they are
the Manager.
As a consequence, Project Managers no longer have inconditional access to all
Tasks and Issues, and will only be able to edit the definitions of Projects
they manage.

This makes it possible for a Project Manager to have private projects that
other users, Project Managers included, will not be able to see. They will
need to be added as followers or team members to able to see it.

Public Projects and their documents are still visible to everyone.
Portal users access rules are kept unchanged.


---------------------
Access Rules summary:
---------------------

Employee Users
    Can see only documents followed or responebile for (in "user_id").
    Can create new documents and edit them while in "New"/"Cancelled" states.

Project Users
    Can edit Project Issues and Tasks in any stage/state.
    Can see all documents for projects they are followers on team memebers.
    Can see only documents followed or assigned to for other projects.

Project Managers
    Can create new projects and edit their attributes.
    Can see all documents (Tasks or Issues) but only for their managed
    projects.
    For the other Projects, will see only followed documents, just like the
    other users.
