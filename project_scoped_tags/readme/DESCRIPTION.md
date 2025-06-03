
Modify tags behavior for projects and tasks, inspired by GitLab’s tag scoping.

## Overview

This module enhances Odoo’s project tagging by introducing the concept of scoped tags:

- Tags can be project-specific (available only to selected projects and their tasks) or global (available everywhere).
- The same tag (by name) can be shared among multiple projects without duplication.
- Tag access is enforced throughout the project and task forms.

## Features

- Project-scoped tags: Each tag has an Available in Projects field; if empty, the tag is global.
- Tag uniqueness: Tag names are unique. If a tag already exists, it is shared with the project rather than duplicated.
- Automatic access management: Removing a tag from a project/task only hide the tag for that project. If no project uses the tag, it is deleted (unless it is made global by a manager).
- Initialization hook: On installation, all tags used by existing projects/tasks are automatically linked to their respective projects’ access list.
- Full domain enforcement: Tags visible for selection in project and task forms are limited to those available for the current project or global tags.
