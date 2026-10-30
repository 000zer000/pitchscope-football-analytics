# Public demonstration readiness

The source repository is public. An application deployment is a separate deliverable;
no screenshot, archive or browser recording is described as a deployed application.

## Account and runtime checks

- Render dashboard redirected to its sign-in page. No compatible Render account
  is currently connected in the available browser session.
- Hugging Face's new Docker Space route redirected to its sign-in page. No
  compatible account is currently connected there either.
- The available Sites runtime runs Cloudflare Workers with a 128 MB isolate and
  no raw TCP. It cannot directly host the existing Python/FastAPI/psycopg stack.
  Replacing this backend with a static imitation is not an acceptable deployment.
- Render's free database expires after 30 days; free service filesystems are
  ephemeral. A permanent-data claim would be misleading.

Sources checked 30 October 2026:
https://render.com/docs/free
https://huggingface.co/docs/hub/spaces-sdks-docker

No paid resource, payment card, subscription or domain was created. Connecting
an appropriate hosting account is required before deployment can proceed.

## Provider-rights gate

Code publication does not redistribute the raw dataset. The current local event
API returns original provider attributes, including shot freeze-frame information.
The StatsBomb User Agreement restricts raw-data redistribution. Do not expose this
API publicly without resolving provider permission or designing and verifying a
restricted analysis-only response contract. Attribution/logo alone do not waive
that restriction. See docs/data-rights.md for the exact source agreement.

## Required deployment checks once an account and rights are available

Use the working backend and isolated PostgreSQL database. Configure only HTTPS
origins, bind database privately, keep credentials in platform secrets, and keep
all import/rebuild commands out of HTTP. Bound events and PDF work; the application
currently caps simultaneous PDF generation at two requests per process (429 with
Retry-After when busy). That is not a distributed abuse-prevention system.

Restore the dataset from the pinned manifest using the administrative CLI. Never
publish a database dump/raw cache in a public repository, image or CI artifact.
Use durable storage or document deterministic restoration and cold-start cost.
Verify search, reference population, match inspection and a non-empty correct PDF
from the actual HTTPS URL before declaring the deployment usable.
