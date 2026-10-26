# 👋 从这里开始 / Start here

**只需要三步。/ Three steps.**

## 1. 把仓库交给 Claude

任选一种：

| 你用的是 | 怎么做 |
|---|---|
| **Claude Code**（终端） | `git clone https://github.com/smartestjamie-art/job-apply-kit.git && cd job-apply-kit && claude` |
| **Claude 桌面端 / Cowork** | 下载仓库（GitHub 页面 Code → Download ZIP）并解压 → 在 Claude 桌面端「连接文件夹」选中这个文件夹 |
| **只能聊天的 Claude（claude.ai）** | 把仓库链接发给 Claude，或者上传 ZIP；Claude 会生成资料文件让你下载保存（填表需要浏览器扩展，见第 3 步） |

## 2. 对 Claude 说一句话

> **请读 CLAUDE.md，带我开始设置。**
> *Please read CLAUDE.md and walk me through setup.*

（Claude Code 里也可以直接输入 `/setup`。）

Claude 会：
1. 请你提供简历 PDF，自动读出姓名、教育、经历、项目；
2. 分 8 轮问你补充信息（每轮最多 4 个问题）；
3. 生成 `profile/profile.yaml` 并校验；
4. 创建你的私人投递表 `data/applications.xlsx`、JD 存档、进度日志和**填表速查卡**；
5. 帮你配置自动搜索（可以直接用伦敦科技类预设，或按你的城市和方向改）；
6. **创建三个定时任务**：每天找岗位、每天查邮箱、每周两次查校招开放（你同意后才创建）；
7. 陪你走一次真实投递。

整个过程约 20–40 分钟。之后每天早上你会收到新岗位推荐和邮件进展。

## 3. 日常使用

| 你说 | Claude 做 |
|---|---|
| 发一个岗位链接 | 查重 → 打分 → 选简历/写求职信 → 在官网填表，**停在提交前** |
| “提交了” | 记录到投递表 + 存 JD 原文 + 写进度 |
| （每天早上自动） | 新岗位推荐、邮件进展、校招开放提醒 |
| “投 + 公司名” | 从早上的推荐里直接开始填表 |
| “查邮件” / “校招开了没” | 立刻手动跑一次 |
| “找岗位” | 按你的方向搜索新岗位，给出打分表 |
| “周报” | 统计、待办、截止日期 |
| “准备 #12 的面试” | 生成针对该岗位的准备笔记 |
| “我换了手机号” | 更新资料并重新生成速查卡 |

**需要的连接**
- 网页填表、校招站点搜索：Chrome 安装 **Claude in Chrome** 扩展（或用桌面端内置浏览器）。没有也能用：Claude 告诉你每个字段填什么，你自己粘贴。
- 每日查邮箱：在 Claude 设置里连接 **Gmail**。
- 定时任务要读写你电脑上的文件夹：运行时电脑要开着、Claude 桌面端要开着。

---

### 你需要知道的
- Claude **不会**替你点最终提交、不会输入密码、不会替你注册登录、不会编造经历。
- 法律声明、隐私同意、电子签名等永远由你本人完成。
- 你的资料只保存在本地 `profile/`、`cv/`、`data/`，这些文件夹已被 `.gitignore` 排除，不会上传到 GitHub。
- 想先看看填好的资料长什么样：[`examples/profile.example.yaml`](examples/profile.example.yaml)（虚构人物）。
