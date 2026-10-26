"""Build the three scheduled-task prompts from templates + your profile + config/search.yaml.

  python scripts/render_schedules.py [--repo-path "/Users/you/job-apply-kit"]

--repo-path: the folder's path ON YOUR COMPUTER (default: this folder's path here).
Writes data/schedules/{daily-job-search,email-check,scheme-watch}.md and schedules.json
(name, cron expression with CRON_TZ, prompt file, connectors needed). Claude uses
schedules.json to create the scheduled tasks during setup.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import ROOT, SCHEDULES, load_profile, load_search, write_json  # noqa: E402

DOW = {"sun": 0, "mon": 1, "tue": 2, "wed": 3, "thu": 4, "fri": 5, "sat": 6}
JOBS = [
    ("daily_job_search", "daily-job-search", "Daily job search", ["web search", "browser (for campus sites / LinkedIn)"]),
    ("email_check", "email-check", "Morning email job check", ["Gmail"]),
    ("scheme_watch", "scheme-watch", "Graduate scheme watch", ["web search", "browser"]),
]
LANG = {"zh": "Chinese (简体中文)", "en": "English"}


def cron(entry, tz):
    hh, mm = (entry.get("time") or "08:41").split(":")
    days = entry.get("days", "daily")
    dow = "*" if days in ("daily", None, "*") else ",".join(str(DOW[d[:3].lower()]) for d in days)
    return f"CRON_TZ={tz} {int(mm)} {int(hh)} * * {dow}" if tz else f"{int(mm)} {int(hh)} * * {dow}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-path", default=str(ROOT))
    a = ap.parse_args()
    p, s = load_profile(), load_search()
    idt = p.get("identity") or {}
    name = idt.get("preferred_name") or idt.get("legal_first_name") or "the user"
    sch, rep = s.get("schedule") or {}, s.get("report") or {}
    tz = sch.get("timezone", "")
    values = {
        "{{NAME}}": name, "{{REPO_PATH}}": a.repo_path,
        "{{LANG}}": LANG.get(rep.get("language", "zh"), rep.get("language", "zh")),
        "{{TOP_N}}": str(rep.get("apply_today_top_n", 3)), "{{MAX_DOUBTFUL}}": str(rep.get("max_doubtful_items", 5)),
        "{{NOTIFY}}": sch.get("notify", "on_change"),
        "{{MAILBOX}}": (s.get("email_check") or {}).get("mailbox") or idt.get("email", ""),
    }
    SCHEDULES.mkdir(parents=True, exist_ok=True)
    out = []
    for key, fname, label, needs in JOBS:
        entry = sch.get(key) or {}
        if not entry.get("enabled", False):
            continue
        text = (ROOT / "templates" / "schedules" / f"{fname}.md").read_text(encoding="utf-8")
        for k, v in values.items():
            text = text.replace(k, v)
        dest = SCHEDULES / f"{fname}.md"
        dest.write_text(text, encoding="utf-8")
        out.append({"name": label, "cron": cron(entry, tz), "prompt_file": str(dest.relative_to(ROOT)),
                    "needs": needs})
        print(f"✓ {label:<26} {cron(entry, tz):<34} → {dest.relative_to(ROOT)}")
    write_json(SCHEDULES / "schedules.json", out)
    print(f"\n已写入 / written: {(SCHEDULES / 'schedules.json').relative_to(ROOT)}")
    if not tz:
        print("⚠ schedule.timezone 为空：cron 将按服务器时区（通常是 UTC）运行。")


if __name__ == "__main__":
    main()
