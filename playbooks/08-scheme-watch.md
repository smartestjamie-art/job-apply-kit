# 08 · 校招项目监测 / Graduate-scheme watch

用于定时任务（默认每周一、周四）或用户说“看看校招开了没”。只搜索和汇报，不填任何申请。
目的：大公司的毕业生项目通常有固定开放季，开放后名额先到先得——要在开放当天知道。

---

## 第 1 步 · 读配置和状态

- 名单：`config/search.yaml` → `scheme_watch.watchlist`（按组）。跳过 `filters.blacklist_companies`。
- 去重：`python scripts/dedup_list.py`（已投的项目不再报）。
- 上次的状态：`python scripts/scheme_state.py list`。

## 第 2 步 · 逐个核实（官网为准）

对每个公司/项目，在**官方页面**上确认本期（下一届）项目：
- 状态：`open` / `closed` / `opens-soon` / `unknown`
- 开放日期、截止日期（或“滚动录取 / 先到先得”）
- **毕业生能否申请**的原话（“final year only”“graduated within N years”“completed degree”等），对照 `candidate.status`
- 国籍/工作许可原话（按 `candidate.ineligible_if` 判断）
- 地点、直接申请链接、推荐简历版本

聚合网站上的旧信息不算数。官方页面打不开 → 用 `--status unknown` 更新（脚本会保留上次核实的状态，不算变化），并写进“覆盖与问题”。页面上没写截止日期就不传 `--closes`，脚本保留上次的日期。

## 第 3 步 · 写入状态并找变化

每个项目运行一次：
```bash
python scripts/scheme_state.py update "<公司> — <项目名>" --status open --opens 2026-10-01 --closes 2026-11-30 --url https://...
```
脚本会输出 `NEW` / `CHANGED` / `same` / `unknown`。只汇报 NEW 和 CHANGED（`unknown` 写进“覆盖与问题”），再加上：
```bash
python scripts/scheme_state.py due --days 14     # 14 天内截止的开放项目
```

## 第 4 步 · 汇报（只报变化）

```
<标题行：本期有 N 个项目开放/状态变化 / 全部项目状态无变化>

【状态变化/新开放】
公司 — 项目 — 地点 — 开放/截止 — 毕业生能否申请（原话）— 签证原话 — 链接 — 推荐简历
回复“投 + 公司名”我就开始填表。

【即将截止】（14 天内，一行一个）

【可能不符合】（最多 5 条，带原话）

【覆盖与问题】查了哪些、哪些打不开或未核实
```
没变化的已关闭项目不要重复列出。

## 第 5 步 · 收尾

`data/progress.md` 追加一行（定时任务里这是 scheme state 之外唯一可以写的地方）。通知按 `schedule.notify`：`on_change` = 有项目开放或 14 天内截止时才发。
