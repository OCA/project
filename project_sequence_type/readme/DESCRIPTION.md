This module lets each project type define its own sequence, so projects
get a different numbering depending on their type.

It is a glue module between `project_sequence` and `project_type` and is
installed automatically when both are present.

Projects whose type has no sequence (or projects without a type) keep
using the default project sequence provided by `project_sequence`.
