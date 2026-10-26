"""Check config/search.yaml.

  python scripts/validate_search.py [--search path]
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import PROFILE, load_profile, load_search  # noqa: E402

DAYS = {"mon", "tue", "wed", "thu", "fri", "sat", "sun"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--search")
    a = ap.parse_args()
    s = load_search(a.search)
    err, warn = [], []
    sch = s.get("schedule") or {}
    tz = sch.get("timezone")
    if not tz:
        err.append("schedule.timezone 为空 / empty (e.g. Europe/London)")
    else:
        try:
            from zoneinfo import ZoneInfo
            ZoneInfo(tz)
        except Exception:  # noqa: BLE001
            err.append(f"schedule.timezone 无效 / invalid: {tz}")
    for k in ("daily_job_search", "email_check", "scheme_watch"):
        e = sch.get(k) or {}
        if e.get("enabled"):
            if not re.fullmatch(r"\d{1,2}:\d{2}", str(e.get("time", ""))):
                err.append(f"schedule.{k}.time 应为 HH:MM")
            d = e.get("days", "daily")
            if d != "daily" and not (isinstance(d, list) and set(x[:3].lower() for x in d) <= DAYS):
                err.append(f"schedule.{k}.days 应为 daily 或 [mon, thu] 这样的列表")
    c = s.get("candidate") or {}
    if c.get("status") not in ("graduated", "student"):
        err.append("candidate.status 应为 graduated 或 student")
    if not (s.get("locations") or {}).get("primary"):
        err.append("locations.primary 为空 / empty")
    dirs = [d for d in s.get("directions") or [] if isinstance(d, dict) and d.get("id")]
    if not dirs:
        err.append("至少需要一个搜索方向 / at least one direction")
    cv_ids = set()
    if PROFILE.exists():
        cv_ids = {v.get("id") for v in load_profile().get("cv_variants") or [] if isinstance(v, dict)}
    for d in dirs:
        if not d.get("keyword_sets"):
            warn.append(f"方向 {d['id']} 没有 keyword_sets")
        if cv_ids and d.get("cv") not in cv_ids:
            err.append(f"方向 {d['id']} 的 cv={d.get('cv')!r} 不在 profile.cv_variants 里 {sorted(x for x in cv_ids if x)}")
    src = s.get("sources") or {}
    if not any((src.get("ats_boards") or {}).values()):
        warn.append("sources.ats_boards 为空：每日搜索将不做 ATS 批量扫描")
    if (sch.get("email_check") or {}).get("enabled") and not (s.get("email_check") or {}).get("mailbox"):
        warn.append("email_check.mailbox 为空：将使用 profile 里的邮箱")
    if (sch.get("scheme_watch") or {}).get("enabled") and not (s.get("scheme_watch") or {}).get("watchlist"):
        err.append("scheme_watch 已启用但 watchlist 为空")
    for w in warn:
        print("WARNING ", w)
    for e in err:
        print("ERROR   ", e)
    if err:
        print(f"\n✗ {len(err)} 个错误 / errors")
        sys.exit(1)
    print(f"\n✓ 搜索配置校验通过 / search config OK ({len(warn)} warnings)")


if __name__ == "__main__":
    main()
