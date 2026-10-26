"""Generate data/form_cheatsheet.md: every common form field with the value to use.

  python scripts/make_cheatsheet.py [--profile path] [--out path]
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import CHEATSHEET, DATA, load_profile, today  # noqa: E402


def g(d, dotted, default=""):
    for k in dotted.split("."):
        if not isinstance(d, dict):
            return default
        d = d.get(k)
    return default if d in (None, "") else d


def row(label, value, note=""):
    v = value if value not in (None, "", []) else "—"
    if isinstance(v, list):
        v = ", ".join(map(str, v))
    return f"| {label} | `{v}` | {note} |"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile")
    ap.add_argument("--out", default=str(CHEATSHEET))
    a = ap.parse_args()
    p = load_profile(a.profile)
    idt = p.get("identity", {}) or {}
    first_single = g(p, "identity.preferred_name") if g(p, "identity.single_first_name_field_uses") == "preferred" \
        and g(p, "identity.preferred_name") else g(p, "identity.legal_first_name")
    pol = g(p, "preferences.diversity_policy", "ask_me")
    L = [f"# 填表速查卡 / Form cheat sheet", "",
         f"> 由 `scripts/make_cheatsheet.py` 于 {today()} 从 profile 生成。改资料后请重新生成。",
         "> 「—」表示资料里没有：先问本人，不要猜。", "",
         "## 姓名与联系方式", "| 字段 | 填写 | 说明 |", "|---|---|---|",
         row("Legal first name / Given name", g(p, "identity.legal_first_name")),
         row("Middle name", g(p, "identity.legal_middle_name")),
         row("Last name / Family name / Surname", g(p, "identity.last_name")),
         row("Preferred name / Known as / Nickname", g(p, "identity.preferred_name"), "有独立栏位时填"),
         row("只有一个 First Name 栏", first_single),
         row("Full name", f"{g(p, 'identity.legal_first_name')} {g(p, 'identity.last_name')}".strip()),
         row("Title", g(p, "identity.title")), row("Pronouns", g(p, "identity.pronouns")),
         row("Date of birth", g(p, "identity.date_of_birth"), "仅必填时使用"),
         row("Nationality", g(p, "identity.nationality")),
         row("Email", g(p, "identity.email")),
         row("Phone（含国家码）", g(p, "identity.phone.number_e164")),
         row("Phone（本国格式）", g(p, "identity.phone.national_format"), "不接受 + 号时"),
         row("Country code", g(p, "identity.phone.country_code")),
         row("Phone（区号单独一栏时）", g(p, "identity.phone.without_country_code_or_zero"), "不带 0、不带国家码"),
         row("Address line 1", g(p, "identity.address.line1")),
         row("Address line 2", g(p, "identity.address.line2")),
         row("City / Town", g(p, "identity.address.city")),
         row("County / State / Region", g(p, "identity.address.county_or_state")),
         row("Postcode / ZIP", g(p, "identity.address.postcode")),
         row("Country", g(p, "identity.address.country")),
         row("LinkedIn", g(p, "identity.links.linkedin")),
         row("GitHub", g(p, "identity.links.github"), "为空表示不填"),
         row("Portfolio / Website", g(p, "identity.links.portfolio")), ""]

    L += ["## 工作许可与求职条件", "| 字段 | 填写 | 说明 |", "|---|---|---|",
          row("Right to work in " + g(p, "right_to_work.target_country", "target country"),
              g(p, "right_to_work.has_right_to_work_now")),
          row("Current immigration status", g(p, "right_to_work.status")),
          row("Visa expiry", g(p, "right_to_work.visa_expiry")),
          row("Require sponsorship now?",
              g(p, "right_to_work.requires_sponsorship_now")
              if g(p, "preferences.sponsorship_question_now") == "answer_from_profile" else "→ 留给本人",
              "策略: " + g(p, "preferences.sponsorship_question_now", "ask_me")),
          row("Require sponsorship in future?",
              g(p, "right_to_work.requires_sponsorship_future")
              if g(p, "preferences.sponsorship_question_future") == "answer_from_profile" else "→ 留给本人",
              "策略: " + g(p, "preferences.sponsorship_question_future", "ask_me")),
          row("Salary expectation", f"{g(p, 'job_search.salary_expectation.amount')} "
              f"{g(p, 'job_search.salary_expectation.currency')}".strip()),
          row("Earliest start date", g(p, "job_search.earliest_start_date")),
          row("Notice period", g(p, "job_search.notice_period")),
          row("Willing to relocate", g(p, "job_search.willing_to_relocate")),
          row("How did you hear about us", g(p, "standard_answers.how_did_you_hear_default"), "知道真实渠道就填真实的"),
          row("Previously employed by us", g(p, "standard_answers.previously_employed_by_company")), ""]

    L += ["## 教育", "| 学校 | 学位/体系 | 专业（下拉备选） | 起止 | 状态 | 成绩 |", "|---|---|---|---|---|---|"]
    for e in p.get("education") or []:
        if not isinstance(e, dict) or not e.get("school"):
            continue
        subj = e.get("subject", "")
        if e.get("subject_fallback") and e.get("subject_fallback") != subj:
            subj += f"（{e['subject_fallback']}）"
        grade = e.get("grade") or (f"predicted {e['predicted_grade']}" if e.get("predicted_grade") else "—")
        if e.get("subjects"):
            grade = "; ".join(f"{s.get('name')} {s.get('grade')}" for s in e["subjects"])
        L.append(f"| {e.get('school')} | {e.get('degree') or e.get('qualification_system', '')} | {subj} | "
                 f"{e.get('start', '')}–{e.get('end', '')} | {e.get('status', '')} | {grade} |")
    L.append("")

    L += ["## 经历"]
    for x in p.get("experience") or []:
        if isinstance(x, dict) and x.get("company"):
            L += [f"**{x.get('title')} · {x.get('company')}** ({x.get('type', '')}, {x.get('city', '')} "
                  f"{x.get('country', '')}, {x.get('start', '')}–{x.get('end', '')}, industry: {x.get('industry', '')})"]
            L += [f"- {b}" for b in x.get("bullets") or []] + [""]
    L += ["## 项目"]
    for x in p.get("projects") or []:
        if isinstance(x, dict) and x.get("name"):
            L += [f"**{x.get('name')}** ({x.get('type', '')}, {x.get('year', '')}) — {', '.join(x.get('stack') or [])}"]
            L += [f"- {b}" for b in x.get("bullets") or []]
            L += [f"- 数据 / metric: {m}" for m in x.get("metrics") or []] + [""]

    sk = p.get("skills") or {}
    L += ["## 技能与语言", "| 类别 | 内容 |", "|---|---|"]
    for k, v in sk.items():
        if v:
            L.append(f"| {k} | {', '.join(v)} |")
    for s in p.get("spoken_languages") or []:
        if isinstance(s, dict) and s.get("language"):
            L.append(f"| Language: {s['language']} | {s.get('level', '')} |")
    L.append("")

    L += ["## 简历版本", "| id | 文件 | 什么时候用 |", "|---|---|---|"]
    for c in p.get("cv_variants") or []:
        if isinstance(c, dict) and c.get("path"):
            L.append(f"| {c.get('id')} | `{c['path']}` | {c.get('use_when', '')} |")
    L.append("")

    L += [f"## 多样性 / 平等机会问卷（策略：{pol}）", "| 字段 | 填写 |", "|---|---|"]
    sa = p.get("standard_answers") or {}
    for k in ["gender", "gender_identity_same_as_birth", "ethnicity", "disability", "religion", "sexual_orientation",
              "marital_status", "veteran_status", "school_type_11_18", "parents_degree", "free_school_meals",
              "household_income_support", "main_earner_occupation_at_14"]:
        if pol == "prefer_not_to_say_all":
            v = "Prefer not to say"
        elif pol == "ask_me":
            v = "→ 问本人"
        else:
            v = sa.get(k) or "Prefer not to say"
        L.append(f"| {k} | `{v}` |")
    L.append("")

    ab = p.get("answer_bank") or {}
    L += ["## 答题素材", f"- 自我介绍：{ab.get('elevator_pitch') or '—'}",
          f"- 为什么选这个方向：{ab.get('why_this_field') or '—'}",
          f"- 优势：{', '.join(ab.get('strengths') or []) or '—'}",
          f"- 待提升：{ab.get('development_area') or '—'}"]
    for s in ab.get("stories") or []:
        if isinstance(s, dict) and s.get("title"):
            L.append(f"- 故事「{s['title']}」 S: {s.get('situation')} T: {s.get('task')} "
                     f"A: {s.get('action')} R: {s.get('result')}")
    L += ["", "## 永远留给本人", *[f"- {x}" for x in p.get("never_fill_for_me") or []], ""]

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"✓ 已生成 / written: {out}")


if __name__ == "__main__":
    main()
