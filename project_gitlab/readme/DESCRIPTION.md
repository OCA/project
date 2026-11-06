GitLab bridge for the `project_git` connector.

It recognizes and authorizes GitLab webhook requests (push, merge
request, pipeline events), maps GitLab users to Odoo users, tracks the
CI pipeline status of the merge requests, deploys the webhook on the
repository from the Odoo project form and can retry the latest
`odoo_sh_deploy` CI job.

Any GitLab instance is supported (gitlab.com or self-hosted), with one
API token per instance.
