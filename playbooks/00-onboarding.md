# 00 · 新用户引导 / Onboarding

目标：用 15–30 分钟和用户一起建好 `profile/profile.yaml`，校验通过，初始化 `data/`，最后陪用户走一次真实（或演练）投递。

**原则**
- 一次只问一组问题（≤4 个）。有 AskUserQuestion 之类的选择题工具就用它，没有就用编号列表提问。
- **先读简历再提问**：能从简历读到的就预填，只让用户确认或修改，别让用户重复打字。
- 不知道的字段留空 `""`，绝不猜。所有数字（成绩、指标、薪资）必须由用户确认。
- 每完成一轮就写回 `profile/profile.yaml`（不要等到最后），防止对话中断丢失。
- 敏感字段（生日、族裔、残疾、性取向等）明确告诉用户“可以选择不提供”。

---

## 第 1 步 · 环境检查（2 分钟）

1. 告诉用户这套工具会做什么、不会做什么（复述 CLAUDE.md 硬规则 1–4，简短）。
2. 确认运行环境：
   - **Claude Code**：在仓库目录里运行。运行 `pip install -r requirements.txt`。
   - **Claude Cowork / 桌面端**：让用户在桌面端「连接文件夹」选中这个仓库文件夹；Python 脚本在电脑上或云端工作区运行都可以。
   - 网页填表需要 **Claude in Chrome** 扩展。没有也能用：Claude 负责生成每个字段的答案，用户自己粘贴。
3. 运行 `python scripts/status.py --setup-check`，把结果用一句话告诉用户。

## 第 2 步 · 简历（3 分钟）

1. 请用户把简历 PDF 放进 `cv/`（或直接发到对话里，你再存进去）。多个方向的简历：每个方向一个子文件夹，例如 `cv/software/Your Name.pdf`、`cv/data/Your Name.pdf`。**同一个人所有版本的文件名一致**（上传时招聘方看到的就是这个名字），不要带 copy、v2、final 之类字样。
2. 读取简历：`python scripts/extract_cv.py cv/<文件>.pdf`（输出纯文本），或直接读 PDF。
3. 从简历预填：姓名、联系方式、链接、教育、经历、项目、技能、语言。先写进 profile，再在下一步让用户确认。

## 第 3 步 · 逐轮访谈

按顺序，每轮问完立即写回 profile。括号里是对应的 profile 字段。

**第 1 轮 · 基本信息（identity）**
- 法定姓名（护照上的写法）和常用名；希望表单里怎么称呼？（`identity.*`, `name_rule`）
- 求职用邮箱、手机号（含国家码）、现居地址（`identity.email/phone/address`）
- LinkedIn / GitHub / 作品集链接；有没有**不想填**的链接？（`identity.links`）
- 称谓和代词（可不填）

**第 2 轮 · 求职目标（job_search）**
- 目标方向（可多个，排优先级），每个方向对应哪份简历？（`job_search.directions`, `cv_variants`）
- 级别：实习 / 应届 / 初级 / 有经验？能接受的最高经验年限要求？（`levels`, `preferences.max_experience_years`）
- 城市、是否接受远程/搬迁；期望薪资（金额+币种）；最早入职日期；通知期（`locations`, `salary_expectation`, `earliest_start`, `notice_period`）
- 不想投的公司或岗位关键词（`exclude_companies`, `exclude_keywords`）

**第 3 轮 · 工作许可与签证（right_to_work）**
- 在目标国家的真实工作许可状态、签证类型、到期日（事实）
- 现在是否需要雇主担保？将来是否需要？（事实）
- **答题策略**：表单问“是否需要担保”时你希望怎么答？“将来是否需要担保”这类问题要不要每次留给你自己答？（`preferences.sponsorship_*`）
- 不提供担保的岗位还投不投？（`preferences.apply_if_no_sponsorship`）
- 参考 `docs/diversity-and-visa.md`。提醒用户：如实作答是本人的责任，Claude 只按用户定的策略执行。

**第 4 轮 · 教育（education）**
- 逐条确认简历里读到的学校、学位、专业、起止年月、成绩/预估成绩、在读还是已毕业。
- 成绩没出的写 `status: expected`，预估成绩必须用户确认后才写进 `predicted_grade`。
- 中学：体系名称（A-Level / IB / 高考 / 其他）、毕业年份、主要科目成绩；海外体系不要硬套成 A-Level。
- 下拉框里常找不到自己的专业：确定一个最接近的备选（`subject_fallback`）。

**第 5 轮 · 经历与项目（experience, projects）**
- 逐条确认简历里的经历和项目；问清公司全称、所在国家、行业、类型（实习/全职/兼职）。
- 每个**数字指标**都问一句“这个数字可以写在申请里吗？”；不确定的删掉或改为定性描述。
- 技能和语言能力（母语/流利/工作水平/基础）。

**第 6 轮 · 多样性与标准答案（standard_answers）**
- 先说明：这些是自愿填写的，可以全部选“不愿透露”。
- 让用户选策略：A 按我给的答案填；B 全部选“不愿透露”；C 每次问我。（`preferences.diversity_policy`）
- 选 A 时逐项确认：性别、族裔、残疾、宗教、性取向、婚姻状况、退伍军人、11–18 岁学校类型、父母学历、家庭收入类问题（免费校餐、Income Support、14 岁时家庭主要收入者职业）。
- 渠道题默认答案（“How did you hear about us?”）。

**第 7 轮 · 偏好（preferences）**
- 最低匹配分（默认 3/5）；求职信策略（有字段就写 / 总是写 / 不写）；Optional 字段是否也填满（默认是）。
- 哪些事情一定要留给你自己（在默认清单之外再加的）（`never_fill_for_me`）。
- 交流语言。

**第 8 轮 · 答题素材（answer_bank，可跳过，以后再补）**
- 30 秒自我介绍；为什么选这个方向；2–3 个真实的 STAR 故事（挑战、团队合作、失败与改进）。只整理用户说过的内容，不添油加醋。

## 第 4 步 · 校验与确认

1. 运行 `python scripts/validate_profile.py`。
   - 有 ERROR：回到对应轮次补问。
   - 只有 WARNING：告诉用户哪些是可选项，问要不要补。
2. 用一个简短表格把关键信息给用户过目（姓名、联系方式、目标方向、签证策略、多样性策略、简历版本），请用户回复“确认”。

## 第 5 步 · 初始化工作区

```bash
python scripts/setup_workspace.py      # 创建 data/applications.xlsx, data/JD_archive.md, data/progress.md, data/notes.md
python scripts/make_cheatsheet.py      # 生成 data/form_cheatsheet.md（填表速查卡）
```
把 `data/form_cheatsheet.md` 发给用户看一眼，告诉他以后手动填表也可以直接复制里面的内容。

## 第 6 步 · 第一次投递（演练）

1. 请用户发一个想投的岗位链接（没有就运行 `playbooks/03-find-jobs.md` 找一个）。
2. 按 `playbooks/01-apply.md` 走完整流程，边做边解释每一步。
3. 用户提交后按 `playbooks/02-log-submission.md` 记录，并告诉用户之后只需要说“提交了”。

## 结束语模板

> 设置完成 ✅ 以后你只需要：
> - 发岗位链接 → 我评估并填表，停在提交前
> - 说“提交了” → 我记录
> - 说“找岗位” / “周报” / “准备面试” → 对应功能
> 你的资料只保存在本地 `profile/` 和 `data/`，不会被上传到 GitHub。
