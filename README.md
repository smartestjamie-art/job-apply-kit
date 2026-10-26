# job-apply-kit

**一个由 Claude 驱动的求职 agent：设置一次，之后它每天早上自己找岗位、查邮件、盯校招，你只需要决定投哪个、检查后点提交。**
*A Claude-powered job-search agent: set it up once; every morning it finds new roles, checks your inbox and watches graduate schemes. You decide what to apply for and click Submit yourself.*

> 中文在前，English below. 👉 **新人请直接看 [START_HERE.md](START_HERE.md)**

这套工作流来自一次真实的求职过程（200+ 次投递）。它把“读 JD → 判断值不值得投 → 选简历 → 写求职信 → 在官网填表 → 记录”这条流水线交给 Claude，**提交按钮始终留给你自己按**。

## 每天会发生什么

| 时间（默认） | agent 自动做 | 你收到 |
|---|---|---|
| 每天 08:41 | 按你的方向扫 ATS 看板、校招站点、招聘网站和分层公司名单，去重、早筛、逐个核实资格 | “今日新增 N 个”+ 建议今天投的 1–3 个 |
| 每天 08:52 | 逐封检查求职邮箱，识别拒信/测评/面试/Offer，自动更新投递表 | 邮件进展和截止事项 |
| 周一、周四 08:57 | 检查毕业生项目是否开放，与上次状态对比 | 只报新开放和 14 天内截止的 |
| 你回复“投 + 公司名” | 评估、选简历、写求职信、填表到最后一步 | 一个停在提交前的标签页 |
| 你说“提交了” | 记录到投递表、存 JD 全文、写进度 | “已记录为 #N” |

## 功能

- 🧭 **引导式设置**：Claude 读你的简历，分轮提问，生成并校验你的资料文件
- 🎯 **岗位评估**：查重、匹配打分（1–5）、标出毕业年份/签证/经验年限等硬门槛
- ✍️ **材料**：按方向选简历版本；只用你的真实经历写求职信（可生成 PDF）
- 🖱️ **填表**：在 Workday / Greenhouse / Lever / Ashby / Oleeo / SmartRecruiters 等官方系统填到最后一步
- 📒 **记录**：Excel 投递表 + JD 全文存档 + 进度日志，一条命令完成
- 🔎 **每日找岗位**：分层公司轮换、关键词轮换、ATS 批量扫描（Greenhouse/Lever/Ashby）、大公司校招站点扫描、自动去重、资格原话核实
- 📬 **每日查邮箱**：不靠关键词过滤，逐封判断，自动更新状态，查不到会明确说“未能检查”
- 🎓 **校招监测**：状态文件对比，只报变化
- ⏰ **定时任务**：设置时自动生成三个任务的提示词并帮你创建
- 🗺️ **预设**：伦敦科技类岗位的完整公司/站点/关键词清单，可直接用或改成你的城市
- 📊 **周报 / 面试准备**：现成的操作手册
- 🧱 **踩坑表**：各招聘系统的已知问题和解决办法

## 快速开始

```bash
git clone https://github.com/smartestjamie-art/job-apply-kit.git
cd job-apply-kit
pip install -r requirements.txt
```
然后对 Claude 说：**“请读 CLAUDE.md，带我开始设置。”**（Claude Code 中可用 `/setup`）
桌面端/Cowork、claude.ai 网页版的用法见 [START_HERE.md](START_HERE.md)。

## 目录

| 路径 | 内容 |
|---|---|
| [`START_HERE.md`](START_HERE.md) | 一页上手说明 |
| [`CLAUDE.md`](CLAUDE.md) | 给 Claude 的总指令：状态判断、指令路由、硬规则 |
| [`playbooks/`](playbooks) | 操作手册：设置、投递、记录、找岗位、周报、面试准备、更新资料 |
| [`profile/profile.template.yaml`](profile/profile.template.yaml) | 资料模板（带注释） |
| [`config/search.template.yaml`](config/search.template.yaml) | 自动搜索 / 查邮箱 / 校招监测配置模板 |
| [`presets/`](presets) | 搜索预设（伦敦科技类） |
| [`examples/profile.example.yaml`](examples/profile.example.yaml) | 填好的虚构示例 |
| [`scripts/`](scripts) | 校验、初始化、速查卡、查重、记录、更新状态、统计、读简历、生成求职信 PDF |
| [`docs/`](docs) | 规则、ATS 踩坑表、签证与多样性问题、常见问题 |
| [`templates/`](templates) | 求职信、开放题思路、数据文件模板 |
| [`.claude/commands/`](.claude/commands) | Claude Code 斜杠命令 |
| `cv/`、`profile/profile.yaml`、`config/search.yaml`、`data/` | **你的私人文件**，已被 git 忽略 |

## 脚本速览

```bash
python scripts/status.py --setup-check          # 检查还缺什么
python scripts/validate_profile.py              # 校验资料
python scripts/setup_workspace.py               # 创建 data/（投递表、JD 存档、进度日志）
python scripts/make_cheatsheet.py               # 生成填表速查卡 data/form_cheatsheet.md
python scripts/check_duplicate.py "公司" "岗位"   # 投过没有
python scripts/log_application.py --title ... --company ... --jd-file data/tmp_jd.md
python scripts/update_status.py 12 --status Interview --flow "HR 面 11-10"
python scripts/status.py                        # 统计
python scripts/validate_search.py               # 校验搜索配置
python scripts/ats_sweep.py                     # ATS 批量扫描（网络受限时用 --emit-js / --ingest）
python scripts/dedup_list.py                    # 去重清单
python scripts/scheme_state.py list             # 校招项目状态
python scripts/email_window.py                  # 本次查邮件的时间范围
python scripts/render_schedules.py --repo-path "<电脑上的路径>"   # 生成定时任务提示词
python scripts/install_local_schedule.py        # （可选）本机 cron / launchd 运行
```

## 原则

1. 不替你点最终提交，不发邮件或消息。
2. 不输入密码，不替你注册或登录。
3. 不编造：所有内容来自你的资料文件。
4. 法律声明、隐私/条款同意、电子签名、“信息真实完整”确认由你本人完成。
5. JD 或申请表声明禁止 AI 作答的开放题：只放 `[DRAFT - 请自己改写]` 标记，不写 AI 生成的正文。
6. 你的资料留在本地，不进 git。

## 贡献

欢迎补充新的招聘系统踩坑（`docs/ats-pitfalls.md`）、改进脚本和手册。提交前请确认**没有任何个人信息**。

---

# English

**job-apply-kit** turns Claude into a careful job-search agent. You set up your profile and search config once (Claude reads your CV and interviews you). Every morning three scheduled tasks run: a daily job search (tiered company rotation, ATS board sweep, campus-site sweep, de-duplication, eligibility checks with quoted wording), an inbox check that updates your tracker, and a graduate-scheme watch that reports only changes. For any job you choose, Claude checks for duplicates, scores the fit, picks the right CV, drafts a cover letter from your real experience, fills the employer's official form up to the final step, and — after **you** click Submit — logs it to an Excel tracker, a JD archive and a progress log.

**Start:** clone the repo, `pip install -r requirements.txt`, and tell Claude *"Read CLAUDE.md and walk me through setup."* (or `/setup` in Claude Code). See [START_HERE.md](START_HERE.md).

**Never:** clicks the final Submit, types passwords, creates accounts, fabricates facts, or ticks legal declarations/consents for you. Your profile, CVs and data stay local (git-ignored).

## License
MIT
