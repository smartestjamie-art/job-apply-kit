# data/ — 你的私人运行数据（不会被提交）

运行 `python scripts/setup_workspace.py` 后生成：

| 文件 | 用途 |
|---|---|
| `applications.xlsx` | 投递记录表（唯一权威来源），Summary 表自动统计各状态数量 |
| `JD_archive.md` | 每次投递的 JD 全文，新的在最前 |
| `progress.md` | 进度日志和待办（待办用 `scripts/todo.py` 管理） |
| `notes.md` | 你的个人规则和经验 |
| `form_cheatsheet.md` | 填表速查卡（`scripts/make_cheatsheet.py` 生成） |
| `cover_letters/` | 求职信 |
| `interview_prep/` | 面试准备笔记 |
| `tmp_jd/` | 正在填、还没记录的岗位 JD，每个岗位一个文件；记录后自动删除 |
| `state/` | 搜索和监测的记忆：已汇报的候选（`candidates.json`）、ATS 已见、校招状态、查邮箱时间 |

建议定期备份这个文件夹（例如复制到网盘）。
