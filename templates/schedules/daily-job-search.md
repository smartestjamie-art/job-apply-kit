# Scheduled task: daily job search for {{NAME}}

Automated run; the user is not present. Do not ask questions: make reasonable choices and note them in the report.
SEARCH AND REPORT ONLY: never fill in, start or submit any application, never send any message.
If the user later replies in this conversation (e.g. "投 + 公司名"), they are present: from that reply on, follow `CLAUDE.md` in interactive mode.

## Where the files are
The job-apply-kit folder is `{{REPO_PATH}}` on the user's computer.
- If you are running inside that folder (Claude Code), use it directly.
- If you are a cloud session linked to the user's computer, find it through the computer's shell (e.g. `ls $HOME/mnt/`) and run every script there.
- If you cannot reach the folder at all, say so in the first line of the report and stop.

## What to do
1. Read `CLAUDE.md`, then follow `playbooks/03-find-jobs.md` in **UNATTENDED mode** exactly.
2. Configuration: `config/search.yaml` (directions, sources, filters, schedule tiers) and `profile/profile.yaml` (CV variants, eligibility facts).
3. The only files you may write: `data/state/*` (via the scripts, plus `data/state/ats_raw.json` when the browser sweep is used) and one appended line in `data/progress.md`.

## Report
Write the report in {{LANG}}, following the format in `playbooks/03-find-jobs.md` (headline first; at most {{TOP_N}} "apply today" picks; then other candidates; at most {{MAX_DOUBTFUL}} doubtful items; then coverage and problems).
Notification policy: {{NOTIFY}} (on_change = notify only when there are new candidates or coverage was badly incomplete).
