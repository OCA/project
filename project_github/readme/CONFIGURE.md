Connect your GitHub repositories, step by step:

1. **Configure the base module first**: webhook endpoint, shared
   authorization token and project mapping are documented in
   `project_git`.

2. **Set the `project_github.token` system parameter** to a GitHub
   personal access token (classic or fine-grained). Create the token
   on GitHub from your avatar menu, **Settings > Developer settings >
   Personal access tokens**; in Odoo, with the developer mode
   activated, set the parameter from **Settings > Technical >
   Parameters > System Parameters**. This token lets Odoo call the
   GitHub API: fetch the PR commits, post messages on the PR, deploy
   the webhook.

   PR commit tracking relies entirely on this fetch: without the token
   no PR commit is tracked (the GitHub webhook data does not include
   usable commit information to fall back on).

   A missing token — or the demo default shipped by the module — makes
   the API calls fail with an explicit error: replace it with a real
   token.

3. **Deploy the webhook** with the **Create Webhooks** button on the
   project form (**Project > Configuration > Projects**, open the
   project; to configure it by hand instead, use the repository page on
   GitHub, **Settings > Webhooks**). The webhook is subscribed to push
   and pull request events and uses the authorization token as HMAC
   secret: GitHub signs every payload with it (`X-Hub-Signature-256`
   header) and the module verifies the signature.

4. **Optionally, map GitHub users to Odoo users**: go to **Settings >
   Users & Companies > Users**, open the user and fill the **Github
   Username** field with their GitHub login. The author of each pull
   request is matched against this field and shown on the PR record as
   **Created by User** (left empty when no user matches).
