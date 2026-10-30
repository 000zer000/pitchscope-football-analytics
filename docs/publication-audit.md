# Publication audit

The authenticated account was verified through the connected GitHub profile and
GitHub's /user API: 000zer000, personal account type User. The repository was absent
before creation. No organization repository was used and no existing content was
replaced. Only this project was pushed; no force-push was used.

Tracked files and commit authors were inspected before the first push. The old
unpublished local branch used an automatically generated machine-hostname email.
It was preserved locally, while a separate main branch was created with a clean
root commit and GitHub's public noreply identity. The old history was not pushed.

The public tree excludes .env, raw JSON, databases, installed dependencies, caches,
intermediate work, local paths and credentials. The source manifest contains
identifiers and hashes, not the raw dataset. Example/test passwords are explicit
local placeholders, not production credentials. No authentication token is in Git.

Source code is MIT licensed. Provider data/logo rights remain separate; see
public-demo-readiness.md and data-rights.md. Public code publication does not grant
permission to redistribute the local API's original provider payloads.

CLI sign-in was explicitly approved with the scopes GitHub displayed. GitHub
required user-completed two-factor verification. Credentials were stored by gh
outside the repository; they were not printed, copied into project files or pushed.
