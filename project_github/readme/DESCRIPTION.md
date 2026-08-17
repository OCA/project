GitHub bridge for the `project_git` connector.

It recognizes and authorizes GitHub webhook requests (push and pull
request events, classified by the `X-GitHub-Event` header and signed
with the shared secret), maps GitHub users to Odoo users and deploys
the webhook on the repository from the Odoo project form.

Only `github.com` repositories are supported (no Enterprise base URL).
