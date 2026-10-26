"""Remember every job a search run has reported, so later runs only report what is new
and "投 + 公司名" can find the link again (state: data/state/candidates.json).

  python scripts/candidates.py add --company "Acme" --title "Graduate Software Engineer" \
      --url https://... [--location London] [--cv software] [--tag software_ai/d] \
      [--kind pick|candidate|doubtful] [--source "Acme careers"] [--note "..."]
        # prints NEW (first time: report it) or SEEN (reported before: don't list it as new)
  python scripts/candidates.py find "Acme"            # 按公司找回岗位和链接
  python scripts/candidates.py list [--days 7]        # 最近汇报过的
  python scripts/candidates.py skip "Acme" "Graduate Software Engineer" [--reason "..."]

Same company + same title counts as the same job, even with a different link.
"""
import argparse
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import CANDIDATES, norm, read_json, today, write_json  # noqa: E402

KINDS = ("pick", "candidate", "doubtful")


def key(company, title):
    return f"{norm(company)}|{norm(title)}"


def same_company(a, b):
    a, b = norm(a), norm(b)
    return bool(a and b) and (a == b or a in b or b in a)


def show(v):
    print(f"{v['status']:<9} {v.get('kind', ''):<9} {v['company']} — {v['title']} | {v.get('location', '')} | "
          f"cv {v.get('cv', '')} | first {v['first_reported']} | {v.get('url', '')}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    ad = sub.add_parser("add")
    ad.add_argument("--company", required=True)
    ad.add_argument("--title", required=True)
    ad.add_argument("--kind", choices=KINDS, default="candidate")
    for k in ("url", "location", "cv", "tag", "source", "note"):
        ad.add_argument("--" + k, default="")
    f = sub.add_parser("find")
    f.add_argument("company")
    ls = sub.add_parser("list")
    ls.add_argument("--days", type=int, default=7)
    sk = sub.add_parser("skip")
    sk.add_argument("company")
    sk.add_argument("title")
    sk.add_argument("--reason", default="")
    a = ap.parse_args()
    db = read_json(CANDIDATES, {"jobs": {}})
    jobs = db["jobs"]

    if a.cmd == "add":
        k = key(a.company, a.title)
        rec = {"company": a.company, "title": a.title, "kind": a.kind, "url": a.url, "location": a.location,
               "cv": a.cv, "tag": a.tag, "source": a.source, "note": a.note}
        # "Monzo" on one site, "Monzo Bank" on another: still the same job
        old = jobs.get(k) or next((v for v in jobs.values() if norm(v["title"]) == norm(a.title)
                                   and same_company(v["company"], a.company)), None)
        if old is None:
            jobs[k] = {**rec, "status": "reported", "first_reported": today(), "last_seen": today()}
            print(f"NEW   {a.company} — {a.title}")
        else:
            print(f"SEEN  {a.company} — {a.title} (first reported {old['first_reported']}, "
                  f"{old['status']}, was {old.get('kind', '')})")
            old.update({k2: v for k2, v in rec.items() if v and not old.get(k2)})  # keep what was reported first
            old["last_seen"] = today()
        write_json(CANDIDATES, db)
    elif a.cmd == "find":
        hits = sorted((v for v in jobs.values() if same_company(v["company"], a.company)),
                      key=lambda v: v["last_seen"], reverse=True)
        for v in hits:
            show(v)
        if not hits:
            print("没有找到 / not found — 不是搜索汇报过的岗位，请用户发链接")
    elif a.cmd == "list":
        since = (date.today() - timedelta(days=a.days)).isoformat()
        hits = sorted((v for v in jobs.values() if v["last_seen"] >= since),
                      key=lambda v: v["first_reported"], reverse=True)
        for v in hits:
            show(v)
        print(f"({len(hits)} jobs, last {a.days} days)")
    elif a.cmd == "skip":
        k = key(a.company, a.title)
        v = jobs.setdefault(k, {"company": a.company, "title": a.title, "first_reported": today(),
                                "last_seen": today()})
        v.update({"status": "skipped", "skipped_on": today(), "skip_reason": a.reason})
        write_json(CANDIDATES, db)
        print(f"✓ 已记为不投 / marked skipped: {a.company} — {a.title}")


if __name__ == "__main__":
    main()
