# 03 · 找岗位 / Find jobs

## 输入
`profile.job_search`（方向、关键词、级别、城市、排除项）。用户也可以临时指定方向或公司名单。

## 步骤
1. 用网页搜索按方向关键词 + 城市 + 级别搜索，优先：
   - 公司官网招聘页、官方 ATS（boards.greenhouse.io、jobs.lever.co、jobs.ashbyhq.com、*.myworkdayjobs.com 等）
   - 学校 Careers 平台（需要用户登录的，请用户登录）
   - 行业招聘网站只用来**发现**岗位，投递时回到官网
2. 对每个候选：确认仍开放、确认级别和城市，记下截止日期。
3. 去重：`python scripts/check_duplicate.py "<公司>" "<岗位>"`，已投过的剔除。
4. 剔除 `exclude_companies`、`exclude_keywords` 命中的岗位。
5. 快速打分（同 01-apply 第 2 步，简版）。

## 输出
一张表，按分数和截止日期排序：

| # | 公司 | 岗位 | 城市 | 分数 | 截止 | 链接 | 一句话理由 |
|---|---|---|---|---|---|---|---|

最后问用户：投哪几个？（用户选了之后逐个执行 `01-apply.md`。）

## 定时运行（可选）
用户想每天自动找：在支持定时任务的环境里建一个每日任务，提示词写“读 CLAUDE.md，执行 playbooks/03-find-jobs.md，把结果写进 data/progress.md 并通知我”。只在用户明确要求时创建。
