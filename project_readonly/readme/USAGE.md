To grant read-only access to the project documents, select *Readonly* under the
*Project* privilege in the user form (Settings / Users).

Holding the *Readonly* option grants read-only access to the project documents
on the user, with no create, write or unlink right.

Users holding the group get:

* read access to projects, tasks (including tasks of other users and
  follower-only projects) and tasks analysis;
* the *Projects*, *My Tasks*, *All Tasks* and *Reporting > Tasks Analysis*
  menus of the Project application.

Notes:

* The record visibility is widened to all documents: by default, internal users
  only see the projects they follow or that are not restricted, while users
  holding this group see every project and task.
* Timesheet and analytic accounting widgets are not displayed for users holding
  only this group, as they are reserved for the corresponding feature groups.
* Action buttons on the projects and tasks (e.g. creating tasks, editing
  stages, sharing) are still displayed but raise an access error for users
  holding only this group.
* The To-Do app is auto-installed with the Project app: users holding the group
  can still create and edit their own personal to-dos (tasks without project)
  and their personal task stages.
