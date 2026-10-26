"""Sweep public ATS job boards (Greenhouse / Lever / Ashby) listed in config/search.yaml.

Filters titles and locations, removes roles already in the tracker or seen before,
and prints the NEW postings as a markdown table (also saved to data/state/ats_last.json).
Postings are only marked as seen by --commit, at the end of a run that finished, so a run
that breaks off halfway does not lose them.

Three ways to run, depending on what your environment allows:

  1) Direct (needs internet access to the ATS APIs):
       python scripts/ats_sweep.py
  2) Through a browser tab (when the sandbox blocks these hosts):
       python scripts/ats_sweep.py --emit-js > data/state/ats_sweep.js
     Claude runs that JavaScript in any open browser tab (e.g. via a javascript tool).
     It filters in the browser and returns a short JSON list (title, location, link without
     query string). Save it to a file, then:
       python scripts/ats_sweep.py --ingest data/state/ats_raw.json
  3) Just list the URLs (to fetch some other way):
       python scripts/ats_sweep.py --urls

After the run's report is written:
       python scripts/ats_sweep.py --commit      # mark this run's postings as seen

Options: --all (do not hide previously seen postings), --no-save (trial run: write nothing).
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

# Same normalising and filtering as normalise()/keep() below, run inside the browser so
# only a short list comes back (and no query strings, which the javascript tool may block).
JS = r"""(async () => {
  const targets = __TARGETS__;
  const inc = __INC__, exc = __EXC__, locs = __LOCS__;
  const esc = w => w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const has = (t, w) => new RegExp('(?<![a-z0-9])' + esc(w) + '(?![a-z0-9])').test(t);
  const keep = j => {
    const t = j.title.toLowerCase(), l = j.location.toLowerCase();
    if (inc.length && !inc.some(w => has(t, w))) return false;
    if (exc.some(w => has(t, w))) return false;
    return !locs.length || locs.some(w => l.includes(w));
  };
  const clean = u => (u || '').split(/[?#]/)[0];
  const uniq = a => [...new Set(a.filter(Boolean))].join(' / ');
  const jobs = [], errors = [];
  await Promise.all(targets.map(async t => {
    try {
      const r = await fetch(t.url);
      if (!r.ok) { errors.push(t.key + ' (' + r.status + ')'); return; }
      const p = await r.json();
      let list = [];
      if (t.kind === 'greenhouse') list = (p.jobs || []).map(j => ({id: String(j.id), title: j.title || '',
        location: (j.location || {}).name || '', url: 'https://boards.greenhouse.io/' + t.slug + '/jobs/' + j.id,
        posted: (j.updated_at || '').slice(0, 10)}));
      if (t.kind === 'lever') list = (p || []).map(j => { const c = j.categories || {};
        return {id: String(j.id || ''), title: j.text || '', location: uniq([c.location, ...(c.allLocations || [])]),
          url: clean(j.hostedUrl), posted: j.createdAt ? new Date(j.createdAt).toISOString().slice(0, 10) : ''}; });
      if (t.kind === 'ashby') list = (p.jobs || []).map(j => ({id: String(j.id || ''), title: j.title || '',
        location: uniq([j.location, ...(j.secondaryLocations || []).map(s => s.location), j.isRemote ? 'Remote' : '']),
        url: clean(j.jobUrl), posted: (j.publishedAt || '').slice(0, 10)}));
      for (const j of list) if (keep(j)) jobs.push({key: t.key, ...j});
    } catch (e) { errors.push(t.key + ' (' + e.message + ')'); }
  }));
  return JSON.stringify({jobs, errors});
})()
"""


def boards(cfg):
    b = (cfg.get("sources") or {}).get("ats_boards") or {}
    return [(kind, slug) for kind in API for slug in (b.get(kind) or [])]


def normalise(kind, slug, payload):
    """Turn one board's raw JSON into a list of {id,company,title,location,url,posted}."""
    out = []
    if kind == "greenhouse":
        for j in (payload or {}).get("jobs", []):
            out.append({"id": str(j.get("id", "")), "title": j.get("title", ""),
                        "location": (j.get("location") or {}).get("name", ""),
                        "url": j.get("absolute_url", ""), "posted": (j.get("updated_at") or "")[:10]})
    elif kind == "lever":
        for j in payload or []:
            cat = j.get("categories") or {}
            locs = [cat.get("location") or ""] + list(cat.get("allLocations") or [])
            ts = j.get("createdAt")
            posted = datetime.fromtimestamp(ts / 1000, timezone.utc).date().isoformat() if isinstance(ts, (int, float)) else ""
            out.append({"id": str(j.get("id", "")), "title": j.get("text", ""),
                        "location": " / ".join(dict.fromkeys(l for l in locs if l)),
                        "url": j.get("hostedUrl", ""), "posted": posted})
    elif kind == "ashby":
        for j in (payload or {}).get("jobs", []):
            locs = [j.get("location") or ""] + [s.get("location", "") for s in j.get("secondaryLocations") or []]
            if j.get("isRemote"):
                locs.append("Remote")
            out.append({"id": str(j.get("id", "")), "title": j.get("title", ""),
                        "location": " / ".join(dict.fromkeys(l for l in locs if l)),
                        "url": j.get("jobUrl", ""), "posted": (j.get("publishedAt") or "")[:10]})
    for o in out:
        o["company"], o["board"] = slug, kind
    return out


def has(text, word):
    return re.search(r"(?<![a-z0-9])" + re.escape(word) + r"(?![a-z0-9])", text) is not None


def filters(src):
    return ([x.lower() for x in src.get("ats_title_include") or []],
            [x.lower() for x in src.get("ats_title_exclude") or []],
            [x.lower() for x in src.get("ats_location_include") or []])


def keep(job, src):
    t = job["title"].lower()
    loc = job["location"].lower()
    inc, exc, locs = filters(src)
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
    targets = [{"key": f"{k}:{s}", "kind": k, "slug": s, "url": API[k].format(slug=s)} for k, s in boards(cfg)]
    inc, exc, locs = filters(cfg.get("sources") or {})
    return (JS.replace("__TARGETS__", json.dumps(targets)).replace("__INC__", json.dumps(inc))
            .replace("__EXC__", json.dumps(exc)).replace("__LOCS__", json.dumps(locs)))


def uid(key, j):
    """Board + job id, so the direct and the browser sweep agree on what was seen."""
    return f"{key}:{j['id']}" if j.get("id") else (j["url"] or f"{key}:{j['title']}")


def process(cfg, jobs, errors, boards_ok, show_all=False, save=True):
    """jobs: list of (board key, normalised job)."""
    src = cfg.get("sources") or {}
    applied = applied_keys()
    seen = read_json(SEEN, {})
    new, old = [], 0
    for key, j in jobs:
        slug = key.split(":", 1)[1]
        j = {**j, "company": slug, "board": key.split(":", 1)[0]}
        if not keep(j, src):
            continue
        if any(norm(c) == norm(slug) or norm(slug) in norm(c) for c, t in applied if t == norm(j["title"])):
            continue
        u = uid(key, j)
        if (u in seen or (j["url"] and j["url"] in seen)) and not show_all:  # url = key used before v4
            old += 1
            continue
        new.append({**j, "uid": u})
    new.sort(key=lambda j: j["posted"], reverse=True)
    if save:
        write_json(LAST, {"date": today(), "new": new, "errors": errors, "boards": boards_ok, "committed": False})
    print(f"# ATS sweep {today()} — boards ok: {boards_ok}, failed: {len(errors)}, "
          f"new matches: {len(new)}, previously seen: {old}\n")
    if new:
        print("| Company | Title | Location | Posted | URL |\n|---|---|---|---|---|")
        for j in new:
            print(f"| {j['company']} | {j['title']} | {j['location']} | {j['posted']} | {j['url']} |")
    else:
        print("无新增 / nothing new")
    if errors:
        print("\n失败的看板 / failed boards (slug may have changed or host blocked): " + ", ".join(errors))
    if save and new:
        print("\n运行顺利结束后执行 / when the run has finished: python scripts/ats_sweep.py --commit")


def commit():
    last = read_json(LAST, {})
    if not last.get("new") or last.get("committed"):
        print("没有待标记的岗位 / nothing to commit")
        return
    seen = read_json(SEEN, {})
    for j in last["new"]:
        seen.setdefault(j["uid"], {"first_seen": last.get("date", today()), "title": j["title"], "company": j["company"]})
    write_json(SEEN, seen)
    last["committed"] = True
    write_json(LAST, last)
    print(f"✓ 已标为看过 / marked seen: {len(last['new'])}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit-js", action="store_true")
    ap.add_argument("--ingest")
    ap.add_argument("--urls", action="store_true")
    ap.add_argument("--commit", action="store_true")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--no-save", action="store_true")
    ap.add_argument("--search")
    a = ap.parse_args()
    if a.commit:
        commit()
        return
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
        errors = data.get("errors", [])
        if "jobs" in data:  # filtered list from --emit-js
            jobs = [(j["key"], j) for j in data["jobs"]]
            boards_ok = len({k for k, _ in boards(cfg)}) - len(errors)
        else:  # raw payloads, as saved by older versions
            raw = data.get("raw", data)
            jobs = [(key, j) for key, p in raw.items() for j in normalise(*key.split(":", 1), p)]
            boards_ok = len(raw)
    else:
        raw, errors = fetch_all(cfg)
        if not raw and errors:
            print("⚠ 所有看板都无法直接访问（可能是网络限制）。改用浏览器方式：\n"
                  "  python scripts/ats_sweep.py --emit-js  → 在浏览器标签页执行 → --ingest 结果文件\n")
        jobs = [(key, j) for key, p in raw.items() for j in normalise(*key.split(":", 1), p)]
        boards_ok = len(raw)
    process(cfg, jobs, errors, boards_ok, show_all=a.all, save=not a.no_save)


if __name__ == "__main__":
    main()
