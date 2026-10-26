# 03 · 找岗位 / Daily job search

用于两种情况：用户说“找岗位”（**互动模式**），或者每日定时任务（**无人值守模式**，UNATTENDED）。
配置全部在 `config/search.yaml`；资格事实在 `profile/profile.yaml`。

**无人值守模式的额外规则**：不提问，遇到需要决定的地方选最合理的做法并在汇报里写明；只搜索和汇报，绝不填写或提交任何申请；只写 `data/state/*`（通过脚本）和 `data/progress.md` 的一行。

---

## 第 1 步 · 今天查什么（先算好再开始）

读 `config/search.yaml`，按今天是星期几决定：
- **方向**：`directions[].days` 为 `daily` 的每天查；为列表（如 `[mon, thu]`）的只在那几天查，其他天在汇报里写一句“XX 方向今日不查（周一/周四查）”。
- **时间窗**：每个方向用 `window_days`；如果今天等于 `deep_sweep.day`，该方向改用 `deep_sweep.window_days`。
- **公司**：`sources.tier_a_daily` 全部 + `sources.tier_b_rotation.<今天>`。
- **关键词**：每个方向从 `keyword_sets` 里选 2–3 组，按星期轮换（例如第 N 组 = 星期序号 mod 组数），保证一周内覆盖全部。

## 第 2 步 · 去重清单（必须第一个做）

```bash
python scripts/dedup_list.py
```
得到：已投岗位、已决定跳过、黑名单公司、额外排除。**把这份清单交给每个子 agent。**
同公司同岗位、即使链接不同，也视为已投；只有状态明显变化（例如重新开放）才再次汇报。

## 第 3 步 · ATS 批量扫描（最便宜，先做）

```bash
python scripts/ats_sweep.py
```
- 能直接联网：脚本直接输出新增岗位表。
- 输出“所有看板都无法直接访问”：改用浏览器方式——`python scripts/ats_sweep.py --emit-js` 生成一段 JavaScript，在任意浏览器标签页里执行，把返回的 JSON 存到 `data/state/ats_raw.json`，再运行 `python scripts/ats_sweep.py --ingest data/state/ats_raw.json`。
- 两种都不行：在汇报“覆盖与问题”里写明，继续后面的步骤。
- 失败的看板（404 等）列在汇报里，提示用户更新 slug。
- 公司在英国的岗位很少时，标题笼统的（如 “Software Engineer”）也打开看一眼正文：项目名常只写在正文里。

## 第 4 步 · 校招 / Early Careers 站点（大公司的应届岗位常在单独站点）

逐个打开 `sources.campus_sites`（网页大多是 JavaScript 渲染，搜索和普通抓取读不到，要用浏览器）：
1. 按城市/国家筛选（试试搜索框输入城市名、或地点筛选）。
2. **不要按标题关键词筛**：把该城市的岗位全部列出来，再读正文判断是不是应届岗位（找 “Graduate Programme / early-career / recent graduates / 项目名”）。
3. 用户提到的公司或贴来的链接：先看这家公司有没有单独的 “Campus / Early Careers / Graduates / Students” 入口，再下结论。
4. 发现新的校招站点：记到汇报的“新站点”里，建议用户加进 `sources.campus_sites`。

## 第 5 步 · 聚合网站 + 今日公司

- `sources.aggregators`：用 URL 模板替换 `{KEYWORDS}`，按发布时间排序、限定时间窗。只用于**发现**，核实一律回官网。
- LinkedIn 遇到 429 限流：不要放弃，稍后换一组关键词重试一次；仍不行就用 Indeed 或官网补，并记为覆盖缺口。
- `sources.skip_sites` 里的镜像站一律不用。
- 今日公司（第 1 步算出的 Tier A + Tier B）：直接看官网招聘页。
- 最后才用网页搜索补漏。

## 第 6 步 · 早筛（打开 JD 之前，按标题+公司直接丢）

直接丢掉（不用打开）：
- 去重清单里的；`filters.blacklist_companies`；`filters.exclude_role_types`
- 方向的 `exclude_titles`（Senior/Lead/Manager、实习等）
- `filters.require_named_employer: true` 时的匿名猎头岗位
- 只有 LinkedIn Easy Apply、没有官网入口的
- `candidate.accept_internships: false` 时的 Intern / Placement

**例外**：校招站点上的岗位按正文判断，不按标题早筛。

## 第 7 步 · 必查项（每个通过早筛的候选）

打开**官网上的单个岗位页**，读完整 JD 和资格说明，写下：
- (a) **地点**（官网核实；`locations.flag_outer_areas` 里的偏远地区要标出；非主城市只在 `extra_by_direction` 允许时保留并单独列出）
- (b) **在读/毕业要求**（是否要求在读、未来毕业日期、最后一年学生）。对照 `candidate.status`：已毕业的人遇到“只招在读/未来毕业”→ 不符合。
- (c) **国籍/工作许可原话**（逐字引用；没写就写“未说明”）。按 `candidate.no_sponsorship_roles` 和 `candidate.ineligible_if` 判断。
- (d) **经验要求原话**：硬性要求超过 `candidate.max_experience_years` → 丢；`keep_if_experience_wording` 里的说法 → 保留并标注。
- 岗位必须**确实开放、有申请入口**。核实不了的写“未核实”。
- 打上方向和分组标签（例如 `software_ai/d`），并按 `directions[].cv` 推荐简历版本。

## 第 8 步 · 子 agent 并行（`budget.use_subagents: true` 时）

每个今天要查的方向开一个子 agent，**prompt 必须自包含**，包括：
资格规则（`candidate`）、方向定义（buckets、exclude_titles、keyword_sets）、去重清单、早筛规则、今天的公司和时间窗、校招站点做法、必查项、浏览器提示（见下）、预算（`budget.tool_calls_per_direction`）和提前停止规则。
每个子 agent 记录查过的来源，只返回一份简短的**访问记录**：被拦截、被限流、没拿到数据、或因时间不够跳过的来源（成功的只报数量）。

**浏览器提示**：多个子 agent 共用一个浏览器时，每个子 agent 自己开标签页并在每次调用时用自己的标签页 ID，结束时关闭；网站需要授权先申请；拒绝非必要 Cookie；Workday 页面等 3–4 秒再读文本；链接点不动时用元素引用或截图坐标点标题；浏览器连不上就试一次其他浏览器工具，仍不行就记为“受阻”。

**提前停止**：某方向扫完时间窗 + 今日公司 + 校招站点后没有新的有效候选，就停，汇报“无新增”。不要用勉强的岗位凑数。

## 第 9 步 · 汇报（语言 `report.language`，正文控制在 `report.max_chars` 字以内，不含候选详情）

```
<标题行：今日新增 N 个可投候选 / 今日无新增>

【建议今天投】（最多 report.apply_today_top_n 个）
公司 — 岗位 — 地点 — 推荐简历 — 一句话理由 — 链接
回复“投 + 公司名”我就开始填表。

【其他候选】
公司 | 岗位 | 地点(已核实) | 级别 | 薪资 | 链接 | 在读/毕业要求 | 签证原话 | 经验原话 | 开放确认 | 分组标签
（非主城市的单独列；只写“不提供担保”的打上 [不提供担保] 标签）

【存疑/不符合】（最多 report.max_doubtful_items 条，一行一个：名称 + 原因；其余省略，黑名单和已去重的不列）

【覆盖与问题】一小段：今天查了哪些方向和公司组、扫了多少个 ATS 看板和校招站点、哪些来源受阻/限流、发现的新校招站点、明天轮换会查什么。
```
某个方向没有新增，只在“覆盖与问题”里写一句，不单独开一节。

## 第 10 步 · 收尾

1. `data/progress.md` 追加一行：`- YYYY-MM-DD 每日搜索：新增 N 个（建议投：A、B）`。
2. 通知（`schedule.notify`）：`on_change` = 有新增候选或覆盖严重不全（例如浏览器离线）时才发；`always` 每次都发；`never` 不发。通知第一句 = 标题行。

## 互动模式

用户在对话里说“找岗位”时：同样的流程，但可以问用户想重点看哪个方向；结束时问“投哪几个？”，用户选了之后逐个执行 `01-apply.md`。
