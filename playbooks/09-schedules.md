# 09 · 定时任务 / Scheduled tasks

三个定时任务让这套工具每天自己跑：

| 任务 | 默认时间 | 做什么 | 需要 |
|---|---|---|---|
| 每日找岗位 Daily job search | 每天 08:41 | `playbooks/03-find-jobs.md` | 网页搜索；浏览器（校招站点、LinkedIn） |
| 每日查邮箱 Morning email check | 每天 08:52 | `playbooks/07-email-check.md` | Gmail 连接器 |
| 校招监测 Graduate scheme watch | 周一、周四 08:57 | `playbooks/08-scheme-watch.md` | 网页搜索；浏览器 |

时间和开关在 `config/search.yaml` → `schedule`。避开整点能减少排队延迟。

---

## 创建（设置流程的最后一步，或用户说“帮我设定时任务”）

1. 确认资料和配置都通过校验：
   ```bash
   python scripts/validate_profile.py && python scripts/validate_search.py
   ```
2. 问用户这个文件夹**在他电脑上的完整路径**（Claude Code 里就是当前目录；桌面端可以从已连接文件夹里看到），然后：
   ```bash
   python scripts/render_schedules.py --repo-path "<电脑上的完整路径>"
   ```
   得到 `data/schedules/*.md`（每个任务的完整提示词）和 `data/schedules/schedules.json`（名称 + cron）。
3. 把三个任务的名称、时间、需要的连接器列给用户，**得到明确同意后**再创建。
4. 按环境创建：

**A. Claude 桌面端 / Cowork / claude.ai（推荐，电脑关着也能跑云端部分）**
- 用当前环境的“定时任务”功能（scheduled task）创建：名称 = `schedules.json` 里的 name，时间 = cron，提示词 = 对应 `.md` 文件的**全文**。
- 每次运行都是全新会话，不记得这次对话——所以提示词必须完整（模板已经处理好）。
- 需要读写用户文件夹的任务，要让任务能访问用户电脑（创建时勾选“需要这台电脑”/关联已连接的文件夹），并确认用户电脑在运行时开机、Claude 桌面端开着。
- 查邮箱任务要带上 Gmail 连接器。
- 创建后告诉用户每个任务的审批设置：如果运行时需要人工批准，提醒用户可以在任务设置里改成自动批准（如果组织允许）。

**B. Claude Code（命令行）**
- 优先用 Claude Code 自带的定时/例行任务功能（如果有），提示词同上。
- 或者用本机定时：`python scripts/install_local_schedule.py`（crontab）或 `--launchd`（macOS），**只打印**要添加的内容，由用户自己粘贴安装。需要电脑在那个时间开着。

**C. 都没有**：告诉用户每天早上自己说一句“找岗位”“查邮件”也一样。

5. 在 `data/progress.md` 记一行“定时任务已创建：……”。

## 修改 / 暂停

- 改时间或开关：改 `config/search.yaml` → 重新 `render_schedules.py` → 在定时任务设置里同步更新（时间或提示词）。
- 改了搜索方向、公司名单：**不用**改定时任务——任务每次运行都会重新读 `config/search.yaml`。
- 暂停：在定时任务设置里关掉，或 `schedule.<任务>.enabled: false` 后重新生成。

## 运行出问题时

- 汇报说“未能检查邮箱”：检查 Gmail 连接器是否在这个任务里启用。
- 汇报说找不到文件夹：电脑没开、桌面端没开、或路径变了（重新 `render_schedules.py --repo-path ...` 并更新任务提示词）。
- 汇报里校招站点/LinkedIn 大面积“受阻”：浏览器扩展没连上，或网站需要重新登录。
