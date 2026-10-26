"""OPTIONAL — run the scheduled tasks on your own computer with the Claude Code CLI
(instead of, or in addition to, scheduled tasks in the Claude app).

  python scripts/install_local_schedule.py            # print crontab lines (Linux/macOS)
  python scripts/install_local_schedule.py --launchd  # print macOS launchd plists instead

Nothing is installed automatically: copy what is printed. Requirements:
  - `claude` (Claude Code CLI) installed and logged in;
  - for the email check, a Gmail MCP server configured in Claude Code;
  - your computer awake at the scheduled time.
Logs go to data/logs/. Run render_schedules.py first.
"""
import argparse
import shlex
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import DATA, ROOT, SCHEDULES, read_json  # noqa: E402

PLIST = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.jobapplykit.{slug}</string>
  <key>ProgramArguments</key><array><string>/bin/zsh</string><string>-lc</string><string>{cmd}</string></array>
  <key>StartCalendarInterval</key>{intervals}
  <key>StandardOutPath</key><string>{log}</string>
  <key>StandardErrorPath</key><string>{log}</string>
</dict></plist>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--launchd", action="store_true")
    a = ap.parse_args()
    jobs = read_json(SCHEDULES / "schedules.json", [])
    if not jobs:
        sys.exit("先运行 / run first: python scripts/render_schedules.py")
    logs = DATA / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    for j in jobs:
        slug = Path(j["prompt_file"]).stem
        log = logs / f"{slug}.log"
        cmd = (f"cd {shlex.quote(str(ROOT))} && claude -p \"$(cat {shlex.quote(j['prompt_file'])})\" "
               f"--permission-mode acceptEdits >> {shlex.quote(str(log))} 2>&1")
        parts = j["cron"].split()
        if parts[0].startswith("CRON_TZ="):
            tz, parts = parts[0], parts[1:]
        else:
            tz = ""
        mm, hh, _, _, dow = parts
        if a.launchd:
            days = [None] if dow == "*" else [int(d) for d in dow.split(",")]
            items = "".join(f"<dict><key>Hour</key><integer>{hh}</integer><key>Minute</key><integer>{mm}</integer>"
                            + (f"<key>Weekday</key><integer>{d}</integer>" if d is not None else "") + "</dict>"
                            for d in days)
            print(f"<!-- ~/Library/LaunchAgents/com.jobapplykit.{slug}.plist  then: "
                  f"launchctl load ~/Library/LaunchAgents/com.jobapplykit.{slug}.plist -->")
            print(PLIST.format(slug=slug, cmd=cmd.replace("&", "&amp;").replace(">", "&gt;").replace("<", "&lt;"),
                               intervals=f"<array>{items}</array>", log=log))
            print()
        else:
            if tz:
                print(f"# {j['name']} — times are in {tz[8:]}; make sure your computer uses that time zone")
            print(f"{mm} {hh} * * {dow} {cmd}")
    if not a.launchd:
        print("\n# 添加方法 / to install: crontab -e  然后粘贴上面几行")
    print("\n# 提示：为减少权限确认，可在 .claude/settings.json 里调整 permissions.allow。")


if __name__ == "__main__":
    main()
