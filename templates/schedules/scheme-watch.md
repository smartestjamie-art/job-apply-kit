# Scheduled task: graduate-scheme watch for {{NAME}}

Automated run; the user is not present. Do not ask questions.
SEARCH AND REPORT ONLY: never fill in or submit any application.

## Where the files are
The job-apply-kit folder is `{{REPO_PATH}}` on the user's computer (use it directly, or find it through the linked computer's shell; if unreachable, say so and stop).

## What to do
1. Read `CLAUDE.md`, then follow `playbooks/08-scheme-watch.md` in **UNATTENDED mode** exactly.
2. Watchlist and blacklist: `config/search.yaml` (`scheme_watch`, `filters`). Eligibility facts: `profile/profile.yaml`.
3. The only file you may write is the scheme state, via `scripts/scheme_state.py`.

## Report
In {{LANG}}, changes only, using the format in `playbooks/08-scheme-watch.md`.
Notification policy: {{NOTIFY}} (on_change = notify only when something opened or a deadline is within 14 days).
