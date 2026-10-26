# 投递流程 / Workflow

```
用户给 URL / 岗位名
   ↓
1 打分（技术栈、经验、地点+签证、公司规模）→ 1–5 分；<3 跳过并说明
   ↓
2 选 CV 版本（profile.cv_variants 的优先级）
   ↓
3 写求职信（100–150 字英文；若表单有该字段）
   ↓
4 填表：独立标签页；停在最后一步；用户本人提交
   ↓
5 当场记录：Tracker 一行 + JD 全文存档 + progress 一行
```

## 打分建议
- 技术栈匹配、项目与 JD 的相关度、年限要求（Graduate/Junior 才投）、地点与工作许可、公司规模。
- 明显不搭（要求 3 年以上、行业跨度大）→ 先问用户，不默认跳过也不硬投。
- “不提供 sponsorship” 的岗位是否仍投，由用户决定（在 profile 里写明默认策略）。

## 填表习惯
- 每个申请一个独立标签页，填完不要在同一标签页导航别处。
- 简历自动解析（Autofill with Resume）几乎总会出错：专业名、日期、公司名、姓名，逐字段核对。
- 屏幕截图常有一步延迟：操作后再等一下或再截一次图确认。
- 隐藏的原生 `<select>` + 自定义下拉：优先用 JS 设置 selectedIndex 并触发 change 事件。
- 最后一两个字段遇到 stale reference 报错时，先截图确认页面状态，不要连续重试（有过表单自行提交的案例）。
- 不要用浏览器后退/刷新（部分 ATS 会报 “Duplicate form submission” 并登出）。

## 记录规范
**Tracker 列**：`# | Job Title | Company | Location | Date Applied | Salary | Headcount | Fit Score | Cover Letter(Y/N) | CV Version | Job Source | Flow | Notes | Status`
- Job Source = 发现岗位的渠道（不是 ATS 名称）。
- Flow 只写关键节点 + 日期，如「在线测试 10-31→HR 面试 11-10→结果待定」。
- Summary 表用 COUNTIF 统计 Status，新增行后记得扩展范围。

**JD_archive.md**：每个岗位一个 `## #编号 公司 — 岗位 | 投递日期`，附链接 + 完整 JD 原文（链接会失效，正文必须存）。新条目插在最前面。

**progress.md**：一行一个事件（投递、测评、面试、拒信），写进展与待办，别塞进 CLAUDE.md。
