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
2. 分 7–8 轮问你补充信息（每轮最多 4 个问题，约 15–30 分钟）；
3. 生成 `profile/profile.yaml` 并校验；
4. 创建你的私人投递表 `data/applications.xlsx`、JD 存档、进度日志和**填表速查卡**；
5. 陪你走一次真实投递。

## 3. 日常使用

| 你说 | Claude 做 |
|---|---|
| 发一个岗位链接 | 查重 → 打分 → 选简历/写求职信 → 在官网填表，**停在提交前** |
| “提交了” | 记录到投递表 + 存 JD 原文 + 写进度 |
| “找岗位” | 按你的方向搜索新岗位，给出打分表 |
| “周报” | 统计、待办、截止日期 |
| “准备 #12 的面试” | 生成针对该岗位的准备笔记 |
| “我换了手机号” | 更新资料并重新生成速查卡 |

**网页自动填表**需要在 Chrome 安装 **Claude in Chrome** 扩展。没有扩展也能用：Claude 会告诉你每个字段填什么，你自己粘贴。

---

### 你需要知道的
- Claude **不会**替你点最终提交、不会输入密码、不会替你注册登录、不会编造经历。
- 法律声明、隐私同意、电子签名等永远由你本人完成。
- 你的资料只保存在本地 `profile/`、`cv/`、`data/`，这些文件夹已被 `.gitignore` 排除，不会上传到 GitHub。
- 想先看看填好的资料长什么样：[`examples/profile.example.yaml`](examples/profile.example.yaml)（虚构人物）。
