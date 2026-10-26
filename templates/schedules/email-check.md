# Scheduled task: morning email check for {{NAME}}

Automated run; the user is not present. Do not ask questions.
READ ONLY for email: never reply, forward, delete, archive, label or send anything.

## Where the files are
The job-apply-kit folder is `{{REPO_PATH}}` on the user's computer (see the same rules as the daily search: use it directly, or find it through the linked computer's shell; if unreachable, say so and stop).

## What to do
1. Read `CLAUDE.md`, then follow `playbooks/07-email-check.md` in **UNATTENDED mode** exactly.
2. Mailbox: `{{MAILBOX}}` (Gmail connector). If the mailbox is not reachable or every search returns nothing suspiciously, the first line of the report must say "本次未能检查邮箱 / mailbox not checked" — never report "no news" in that case.
3. You may update the tracker only through `scripts/update_status.py`, append to `data/progress.md`, and run `scripts/email_window.py --done` at the end.

## Report
In {{LANG}}, using the format in `playbooks/07-email-check.md`. Put anything due today or tomorrow first with ⚠️.
Notification policy: {{NOTIFY}}.
