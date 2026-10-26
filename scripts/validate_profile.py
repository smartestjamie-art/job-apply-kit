"""Check profile/profile.yaml for missing or placeholder values.

  python scripts/validate_profile.py [--profile path]

Exit code 0 = no errors (warnings allowed), 1 = errors.
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import ROOT, load_profile  # noqa: E402

REQUIRED = [
    "identity.legal_first_name", "identity.last_name", "identity.email",
    "identity.phone.number_e164", "identity.address.city", "identity.address.country",
    "right_to_work.target_country", "right_to_work.has_right_to_work_now",
    "right_to_work.requires_sponsorship_now",
    "job_search.levels", "job_search.locations",
    "preferences.diversity_policy", "preferences.sponsorship_question_now",
    "preferences.sponsorship_question_future", "preferences.apply_if_no_sponsorship",
]
RECOMMENDED = [
    "identity.phone.national_format", "identity.phone.without_country_code_or_zero",
    "identity.address.line1", "identity.address.postcode", "identity.links.linkedin",
    "job_search.salary_expectation.amount", "job_search.earliest_start_date",
    "standard_answers.how_did_you_hear_default", "answer_bank.elevator_pitch",
]
ENUMS = {
    "preferences.cover_letter": {"when_field_exists", "always", "never"},
    "preferences.diversity_policy": {"fill_from_profile", "prefer_not_to_say_all", "ask_me"},
    "preferences.sponsorship_question_now": {"answer_from_profile", "ask_me"},
    "preferences.sponsorship_question_future": {"answer_from_profile", "ask_me"},
    "preferences.apply_if_no_sponsorship": {"yes", "no", "ask_me"},
    "identity.single_first_name_field_uses": {"legal", "preferred"},
    "right_to_work.has_right_to_work_now": {"yes", "no"},
    "right_to_work.requires_sponsorship_now": {"yes", "no"},
}
PLACEHOLDER = re.compile(r"(\bFILL\b|YOUR_[A-Z_]+|XXXX|\bTODO\b|\bTBD\b|<[^>]+>)")
DIVERSITY = ["gender", "ethnicity", "disability", "religion", "sexual_orientation", "marital_status",
             "school_type_11_18", "parents_degree"]


def get(d, dotted):
    for k in dotted.split("."):
        if not isinstance(d, dict):
            return None
        d = d.get(k)
    return d


def empty(v):
    return v is None or (isinstance(v, str) and not v.strip()) or (isinstance(v, (list, dict)) and not v)


def walk(d, prefix=""):
    if isinstance(d, dict):
        for k, v in d.items():
            yield from walk(v, f"{prefix}.{k}" if prefix else k)
    elif isinstance(d, list):
        for i, v in enumerate(d):
            yield from walk(v, f"{prefix}[{i}]")
    else:
        yield prefix, d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile")
    a = ap.parse_args()
    p = load_profile(a.profile)
    errors, warns = [], []

    for f in REQUIRED:
        if empty(get(p, f)):
            errors.append(f"缺少必填 / missing required: {f}")
    for f in RECOMMENDED:
        if empty(get(p, f)):
            warns.append(f"建议填写 / recommended: {f}")
    for f, allowed in ENUMS.items():
        v = get(p, f)
        if not empty(v) and str(v) not in allowed:
            errors.append(f"取值无效 / invalid value {f}={v!r}; 可选 / allowed: {sorted(allowed)}")

    for path, v in walk(p):
        if isinstance(v, str) and PLACEHOLDER.search(v) and "never_fill_for_me" not in path:
            errors.append(f"仍是占位内容 / placeholder left: {path} = {v!r}")
        if isinstance(v, str) and "example.com" in v and "example" not in str(a.profile or ""):
            warns.append(f"看起来是示例数据 / looks like example data: {path}")

    email = get(p, "identity.email") or ""
    if email and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        errors.append(f"邮箱格式不对 / bad email: {email}")
    phone = get(p, "identity.phone.number_e164") or ""
    if phone and not re.fullmatch(r"\+\d{7,15}", phone.replace(" ", "")):
        errors.append(f"手机号应为 +国家码+号码 / phone should be E.164 like +447700900123: {phone}")

    edu = [e for e in (p.get("education") or []) if isinstance(e, dict) and not empty(e.get("school"))]
    if not edu:
        errors.append("至少需要一条教育经历 / at least one education entry")
    for i, e in enumerate(edu):
        for k in ("start", "end"):
            v = str(e.get(k) or "")
            if v and not re.fullmatch(r"\d{4}-\d{2}(-\d{2})?", v):
                warns.append(f"education[{i}].{k} 建议用 YYYY-MM: {v}")
        if e.get("level") != "secondary" and empty(e.get("status")):
            warns.append(f"education[{i}].status 建议填 completed / expected")

    cvs = [c for c in (p.get("cv_variants") or []) if isinstance(c, dict) and not empty(c.get("path"))]
    if not cvs:
        errors.append("至少需要一份简历 / at least one cv_variants entry with a path")
    for c in cvs:
        fp = ROOT / c["path"]
        if not fp.exists():
            errors.append(f"简历文件不存在 / CV file not found: {c['path']}")
        name = Path(c["path"]).name.lower()
        if any(w in name for w in ("copy", "副本", "final", "v2", "draft")):
            warns.append(f"简历文件名不建议包含 copy/final/v2 等: {c['path']}")
    ids = {c.get("id") for c in cvs}
    for d in (get(p, "job_search.directions") or []):
        if isinstance(d, dict) and d.get("cv") and d["cv"] not in ids:
            errors.append(f"方向 {d.get('name')!r} 引用的简历 id 不存在: {d['cv']}")

    if get(p, "preferences.diversity_policy") == "fill_from_profile":
        for k in DIVERSITY:
            if empty(get(p, f"standard_answers.{k}")):
                warns.append(f"多样性策略为按资料填写，但 standard_answers.{k} 为空（将按 Prefer not to say 处理）")

    for m in [m for pr in (p.get("projects") or []) if isinstance(pr, dict) for m in (pr.get("metrics") or [])]:
        if not re.search(r"\d", str(m)):
            warns.append(f"metrics 里应是具体数字 / metric without a number: {m}")

    for w in warns:
        print("WARNING ", w)
    for e in errors:
        print("ERROR   ", e)
    if errors:
        print(f"\n✗ {len(errors)} 个错误需要补充 / errors to fix, {len(warns)} 个提醒 / warnings")
        sys.exit(1)
    print(f"\n✓ 资料校验通过 / profile OK  ({len(warns)} 个提醒 / warnings)")


if __name__ == "__main__":
    main()
