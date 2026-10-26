# job-apply-kit · 让 Claude 帮你批量、规范地投简历 / Let Claude apply for jobs with you

> 中文在前，English below.

一套从真实求职（200+ 次投递）中沉淀出来的工作流：**你给岗位链接，Claude 帮你打分、写求职信、在官方招聘页把表填到最后一步，你本人点提交，然后自动记录到 Tracker 和 JD 存档。**

## 它能做什么
- 岗位匹配打分（1–5 分），低于 3 分直接告诉你原因并跳过
- 按岗位 JD 生成简短的英文求职信
- 用浏览器（Claude in Chrome）填写 Ashby / Greenhouse / Lever / Workday / Taleo / SmartRecruiters 等表单，**停在最后一步，由你本人提交**
- 每次投完自动更新 Excel Tracker、归档 JD 原文、写进度日志
- 内置各类 ATS 的踩坑经验（见 `docs/ats-pitfalls.md`）

## 5 分钟上手
1. 用 **Claude Cowork / Claude Code**，并装好 **Claude in Chrome** 浏览器扩展。
2. Fork 或下载本仓库，进入目录。
3. `cp profile/profile.template.yaml profile/profile.yaml`，填你自己的信息（**此文件已被 .gitignore，不会上传**）。
4. 把你的简历 PDF 放进 `cv/`（同样不会上传）；多个方向就建多个子文件夹，文件名统一为 `Your Name.pdf`。
5. `python tracker/make_tracker.py` 生成空白 Tracker。
6. 对 Claude 说：“请先读 `CLAUDE.md` 和 `profile/profile.yaml`，然后帮我投这个岗位：<链接>”。

## 目录
| 路径 | 说明 |
|---|---|
| `CLAUDE.md` | 给 Claude 的总指令：硬规则 + 投递流程（入口文件） |
| `profile/profile.template.yaml` | 个人信息与“标准答案”模板 |
| `docs/workflow.md` | 投递流程详解 |
| `docs/rules.md` | 安全规则与填表规则 |
| `docs/ats-pitfalls.md` | 各 ATS 踩坑速查 |
| `docs/diversity-and-visa.md` | 多样性问卷 / 签证类问题的处理方式 |
| `templates/cover-letter.md` | 求职信模板 |
| `tracker/` | Tracker 生成与追加脚本 |

## 重要原则
1. **绝不代替你点最终 Submit / 发送邮件。**
2. **绝不输入密码、不替你注册或登录账号**，需要登录时由你自己完成。
3. **不编造**：所有字段只来自你的 profile，求职信里的数字必须来自你的真实经历。
4. 法律声明、隐私/条款同意、电子签名、“信息真实完整”类确认由你本人完成。
5. 雇主明确禁止用 AI 作答的开放题，只写占位草稿让你重写。

> ⚠️ 请勿提交你的 `profile.yaml`、简历、Tracker 和 JD 存档到公开仓库。`.gitignore` 已默认排除。

---

# English

A battle-tested workflow distilled from 200+ real applications: **you send a job link; Claude scores the fit, drafts a short cover letter, fills the employer's official application form up to the final step, you click Submit yourself, then it logs everything to a tracker and a JD archive.**

## Quick start
1. Use **Claude Cowork / Claude Code** with the **Claude in Chrome** extension.
2. Fork/clone this repo.
3. `cp profile/profile.template.yaml profile/profile.yaml` and fill in your details (git-ignored).
4. Put your CV PDF(s) in `cv/` (git-ignored). One sub-folder per CV variant, each file named `Your Name.pdf`.
5. `python tracker/make_tracker.py` to create a blank tracker.
6. Tell Claude: "Read `CLAUDE.md` and `profile/profile.yaml`, then apply to this job: <url>".

## Principles
Never submit for you · never type passwords or create accounts · never fabricate · legal declarations/consents are yours · "no AI-generated answers" questions get placeholder drafts only.

Keep `profile.yaml`, CVs, trackers and JD archives out of public repos (already git-ignored).

## License
MIT
