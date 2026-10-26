# 01 · 投递一个岗位 / Apply to one job

输入：岗位链接或公司+岗位名。输出：表单填到最后一步、用户本人提交。

## 1. 读 JD 并查重
1. 打开链接（新标签页），把 JD 全文保存到临时文件 `data/tmp_jd.md`（之后存档要用）。
2. 查重：`python scripts/check_duplicate.py "<公司>" "<岗位>"`。
   - 同岗位已投 → 告诉用户状态和日期，默认不重投。
   - 同公司其他岗位被拒过 → 提醒用户（有的公司限制同周期申请次数）。
3. 检查截止日期、地点、是否已关闭。已关闭就告诉用户并停止。

## 2. 匹配评分（1–5 分）
从下面几方面各写一句，再给总分和一句话理由：
- 技术栈/技能与 `profile.skills`、`projects` 的重合度
- 经验年限要求 vs `preferences.max_experience_years`、`job_search.levels`
- 地点、远程、工作许可（结合 `right_to_work`、`preferences.apply_if_no_sponsorship`）
- 学历要求、毕业时间要求（例如“需 2027 年毕业”）
- 硬性门槛（安全审查、国籍、语言、驾照等）

总分 < `preferences.min_fit_score`：说明原因，问用户是否仍要投。
有不确定的硬性门槛（如毕业年份限制）：明确告诉用户，让用户决定。

## 3. 选材料
- 简历：按 `job_search.directions` 和 `cv_variants.use_when` 选一版，告诉用户选了哪版、为什么。
- 求职信：按 `preferences.cover_letter`。需要时按 `templates/cover-letter.md` 写，保存到 `data/cover_letters/<公司>_<岗位>.md`（要上传文件就生成 PDF：`python scripts/make_cover_letter_pdf.py data/cover_letters/xxx.md`）。**只用 profile 里有的事实和数字。**
- 开放题：从 `answer_bank` 改写；雇主禁止 AI 时只写草稿。

## 4. 填表
1. 先查 `docs/ats-pitfalls.md` 中对应系统的坑。
2. 需要登录/注册 → 停下，请用户自己登录，登录后继续。
3. 按 `data/form_cheatsheet.md` 填写。Optional 字段按 `preferences.fill_optional_fields`。
4. 简历自动解析后的内容逐字段核对（姓名、学校、日期、雇主常被解析错）。
5. 下拉框找不到准确选项：选最接近的，并在最后的汇报里列出来。
6. 遇到下面的字段**不填**，记下来交给用户：硬规则 4 + `never_fill_for_me` + `preferences` 里设为 `ask_me` 的项目。
7. 每页填完先截图确认，再点“下一页/保存并继续”。**最后的 Submit 不点。**

## 5. 交给用户
用这个格式汇报：
```
<公司> · <岗位>  已填到最后一步（标签页已打开）
- 简历：<版本>   求职信：<有/无>
- 需要你做：① … ② …（本人专属项目、没把握的字段）
- 我做的选择：渠道=…、下拉近似项=…
检查无误后请你点提交，然后告诉我“提交了”。
```
