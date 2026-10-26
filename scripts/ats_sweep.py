"""Sweep public ATS job boards (Greenhouse / Lever / Ashby) listed in config/search.yaml.

Filters titles and locations, removes roles already in the tracker or seen before,
and prints the NEW postings as a markdown table (also saved to data/state/ats_last.json).

Three ways to run, depending on what your environment allows:

  1) Direct (needs internet access to the ATS APIs):
       python scripts/ats_sweep.py
  2) Through a browser tab (when the sandbox blocks these hosts):
       python scripts/ats_sweep.py --emit-js > data/state/ats_sweep.js
     Claude runs that JavaScript in any open browser tab (e.g. via a javascript tool);
     it returns JSON. Save it to a file, then:
       python scripts/ats_sweep.py --ingest data/state/ats_raw.json
  3) Just list the URLs (to fetch some other way):
       python scripts/ats_sweep.py --urls

Options: --all (do not hide previously seen postings), --no-save (don't update seen state).
"""
import argparse
import json
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import STATE, applied_keys, load_search, norm, read_json, today, write_json  # noqa: E402

API = {
    "greenhouse": "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs",
    "lever": "https://api.lever.co/v0/postings/{slug}?mode=json",
    "ashby": "https://api.ashbyhq.com/posting-api/job-board/{slug}",
}
SEEN = STATE / "seen_jobs.json"
LAST = STATE / "ats_last.json"


def boards(cfg):
    b = (cfg.get("sources") or {}).get("ats_boards") or {}
    return [(kind, slug) for kind in API for slug in (b.get(kind) or [])]


def normalise(kind, slug, payload):
    """Turn one board's raw JSON into a list of {company,title,location,url,posted}."""
    out = []
    if kind == "greenhouse":
        for j in (payload or {}).get("jobs", []):
            out.append({"title": j.get("title", ""), "location": (j.get("location") or {}).get("name", ""),
                        "url": j.get("absolute_url", ""), "posted": (j.get("updated_at") or "")[:10]})
    elif kind == "lever":
        for j in payload or []:
            cat = j.get("categories") or {}
            locs = [cat.get("location") or ""] + list(cat.get("allLocations") or [])
            ts = j.get("createdAt")
            posted = datetime.fromtimestamp(ts / 1000, timezone.utc).date().isoformat() if isinstance(ts, (int, float)) else ""
            out.append({"title": j.get("text", ""), "location": " / ".join(dict.fromkeys(l for l in locs if l)),
                        "url": j.get("hostedUrl", ""), "posted": posted})
    elif kind == "ashby":
        for j in (payload or {}).get("jobs", []):
            locs = [j.get("location") or ""] + [s.get("location", "") for s in j.get("secondaryLocations") or []]
            if j.get("isRemote"):
                locs.append("Remote")
            out.append({"title": j.get("title", ""), "location": " / ".join(dict.fromkeys(l for l in locs if l)),
                        "url": j.get("jobUrl", ""), "posted": (j.get("publishedAt") or "")[:10]})
    for o in out:
        o["company"], o["board"] = slug, kind
    return out


def has(text, word):
    return re.search(r"(?<![a-z0-9])" + re.escape(word) + r"(?![a-z0-9])", text) is not None


def keep(job, src):
    t = job["title"].lower()
    loc = job["location"].lower()
    inc = [x.lower() for x in src.get("ats_title_include") or []]
    exc = [x.lower() for x in src.get("ats_title_exclude") or []]
    locs = [x.lower() for x in src.get("ats_location_include") or []]
    if inc and not any(has(t, x) for x in inc):
        return False
    if any(has(t, x) for x in exc):
        return False
    if locs and not any(x in loc for x in locs):
        return False
    return True


def fetch_all(cfg):
    raw, errors = {}, []
    for kind, slug in boards(cfg):
        url = API[kind].format(slug=slug)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "job-apply-kit"})
            with urllib.request.urlopen(req, timeout=20) as r:
                raw[f"{kind}:{slug}"] = json.loads(r.read().decode("utf-8"))
        except Exception as e:  # noqa: BLE001
            errors.append(f"{kind}:{slug} ({getattr(e, 'code', '') or type(e).__name__})")
    return raw, errors


def emit_js(cfg):
    targets = [{"key": f"{k}:{s}", "url": API[k].format(slug=s)} for k, s in boards(cfg)]
    return ("(async () => {\n"
            f"  const targets = {json.dumps(targets)};\n"
            "  const raw = {}, errors = [];\n"
            "  await Promise.all(targets.map(async t => {\n"
            "    try { const r = await fetch(t.url); if (!r.ok) { errors.push(t.key + ' (' + r.status + ')'); return; }\n"
            "          raw[t.key] = await r.json(); } catch (e) { errors.push(t.key + ' (' + e.message + ')'); }\n"
            "  }));\n"
            "  return JSON.stringify({raw, errors});\n"
            "})()\n")


def process(cfg, raw, errors, show_all=False, save=True):
    src = cfg.get("sources") or {}
    applied = applied_keys()
    seen = read_json(SEEN, {})
    new, old = [], 0
    for key, payload in raw.items():
        kind, slug = key.split(":", 1)
        for j in normalise(kind, slug, payload):
            if not keep(j, src):
                continue
            if any(norm(c) == norm(slug) or norm(slug) in norm(c) for c, t in applied if t == norm(j["title"])):
                continue
            uid = j["url"] or f"{key}:{j['title']}"
            if uid in seen and not show_all:
                old += 1
                continue
            seen.setdefault(uid, {"first_seen": today(), "title": j["title"], "company": slug})
            new.append(j)
    new.sort(key=lambda j: j["posted"], reverse=True)
    if save:
        write_json(SEEN, seen)
        write_json(LAST, {"date": today(), "new": new, "errors": errors, "boards": len(raw)})
    print(f"# ATS sweep {today()} — boards ok: {len(raw)}, failed: {len(errors)}, "
          f"new matches: {len(new)}, previously seen: {old}\n")
    if new:
        print("| Company | Title | Location | Posted | URL |\n|---|---|---|---|---|")
        for j in new:
            print(f"| {j['company']} | {j['title']} | {j['location']} | {j['posted']} | {j['url']} |")
    else:
        print("无新增 / nothing new")
    if errors:
        print("\n失败的看板 / failed boards (slug may have changed or host blocked): " + ", ".join(errors))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit-js", action="store_true")
    ap.add_argument("--ingest")
    ap.add_argument("--urls", action="store_true")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--no-save", action="store_true")
    ap.add_argument("--search")
    a = ap.parse_args()
    cfg = load_search(a.search)
    if a.urls:
        for k, s in boards(cfg):
            print(API[k].format(slug=s))
        return
    if a.emit_js:
        print(emit_js(cfg))
        return
    if a.ingest:
        data = json.loads(Path(a.ingest).read_text(encoding="utf-8"))
        if isinstance(data, str):
            data = json.loads(data)
        raw, errors = data.get("raw", data), data.get("errors", [])
    else:
        raw, errors = fetch_all(cfg)
        if not raw and errors:
            print("⚠ 所有看板都无法直接访问（可能是网络限制）。改用浏览器方式：\n"
                  "  python scripts/ats_sweep.py --emit-js  → 在浏览器标签页执行 → --ingest 结果文件\n")
    process(cfg, raw, errors, show_all=a.all, save=not a.no_save)


if __name__ == "__main__":
    main()
