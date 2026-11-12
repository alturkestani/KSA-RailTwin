> **Document version:** SECURITY.md v1.2 | 12 Nov 2026 | Author: report-writer (R9); PUBLISH_PREP (v1.1: one grep-able contact placeholder, CP7 item 7); PUBLISH_EXPORT (v1.2: contact = GitHub private vulnerability reporting, Tariq's answer Q1) | Status: draft

# Security policy

KSA Rail Twin is a personal, open-source feasibility study maintained by one person. This page says what is in scope, how to report a problem, and which version is supported.

## No secrets in the repository

- The repository holds no API keys, tokens, passwords or credentials, and none may be added.
- Where a step needs a key (none of the default pipeline does), the key is read from an environment variable named in the documentation, never from a tracked file, a URL or a command line saved in a script.
- `.env` and `.env.*` are gitignored. So are `data/`, `runs/`, `logs/` and `movies/`, which may hold local material.
- No absolute home paths in tracked files.

If you find a secret, a credential or personal data in any tracked file or in the git history, report it privately (below); do not copy it into an issue.

## Scope

In scope:

- **The code**: the Python packages, scripts, the `Makefile` and the orchestration scripts in this repository.
- **CI**: `.github/workflows/ci.yml` (it installs the locked dependencies and runs `make test` without data).
- **The dashboard API** (`api/`): read-only and file-backed (GET only). `make dashboard` binds it to `127.0.0.1`, and the API itself makes no external network calls. It serves the built web app from `web/dist`.

Worth knowing when you assess a report:

- The dashboard web app (`web/`) runs in your browser and loads its base map style and tiles from a public tile service (`BASEMAP_STYLE_URL` in `web/src/config.ts`); that request comes from the browser, not from the API.
- Some data-build modules download public datasets when a maintainer runs them by hand (they are never run by the tests or CI); each download is recorded in `cities/ksa/sources.yaml` with its SHA-256.

Out of scope: third-party services and datasets themselves (report those to their owners), deployments by anyone else, and the study's findings (questions about a figure or method are ordinary issues, not security reports).

## How to report

Report privately to the maintainer, Tariq Alturkestani, through GitHub's **private vulnerability reporting** on this repository: the **Security** tab, then **Report a vulnerability** (https://github.com/alturkestani/KSA-RailTwin/security/advisories/new). The report is visible only to you and the maintainer. There is no email contact. Please do **not** open a public issue for a security problem.

Please include:

- what is affected (file, commit or tag, command);
- how to reproduce it, step by step;
- what an attacker could do with it, as you see it;
- any suggested fix;
- whether, and how, you would like to be credited.

The maintainer will acknowledge the report, investigate it and tell you the outcome. Please allow time for a fix before any public disclosure. There is no bug bounty and no payment for reports.

## Supported versions

Only the latest tagged milestone (`r<n>`; see `CHANGELOG.md`) is supported. Fixes go into the next milestone; earlier tags are not patched.
