Odoo stores the project top menu settings (the bar of buttons above the
tasks of a project, such as Tasks, Timesheets and Sales Orders) per user and
per project. Each project you open, also from a sales order, starts with the
top menu hidden and with only its first button, and the buttons you chose on
one project are not used on the next one.

This module keeps one choice per user for all projects:

- The top menu is shown by default. When you hide it, it stays hidden on the
  next projects until you show it again.
- The buttons you turn on or off in the top menu dropdown are used on every
  project that has them. A button a project does not have is skipped.

The choice is kept in the browser's local storage, so it applies at once
without extra server calls. It is also saved in the user settings as Odoo
does. Top menus of other models are not changed.
