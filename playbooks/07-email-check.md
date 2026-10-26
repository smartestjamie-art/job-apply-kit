# 07 · 查邮箱 / Email check

用于每日定时任务（无人值守）或用户说“查一下邮件”。需要 Claude 已连接 Gmail（或其他邮箱连接器）。

**只读邮件**：绝不回复、转发、删除、归档、加标签或发送任何内容。

---

## 第 1 步 · 确认邮箱能用

1. 邮箱 = `config/search.yaml` 的 `email_check.mailbox`（为空就用 `profile.identity.email`）。
2. 先做一次简单搜索（例如 `to:<邮箱>` 或最近 1 天）。
   - 连接器不存在、报错、或明显应该有邮件却全部为空 → 汇报第一行写 **“本次未能检查邮箱”** 并说明原因。**绝不能把“查不到”当成“没有新邮件”。**

## 第 2 步 · 拉取全部新邮件（不用关键词过滤）

```bash
python scripts/email_window.py      # 输出类似 after:2026/10/24
```
用这个日期范围搜索**全部**邮件。不要用 `subject:(application OR interview …)` 之类的关键词过滤——拒信常用 “Thanks for your interest in …” 这样不含关键词的标题，过滤会漏。用 `after:YYYY/MM/DD` 比 `newer_than:2d` 更可靠。

## 第 3 步 · 逐封判断

对列表里的**每一封**看发件人 + 主题 + 摘要：
- 明显无关（推广、newsletter、账单、订阅确认、验证码）→ 跳过，不用展开。
- 可能和求职有关（公司域名、ATS 系统发信如 Workday/Greenhouse/Lever/Ashby/SmartRecruiters/Oleeo/Taleo/Teamtailor、提到岗位或申请）→ **打开全文**。
- 拿不准 → 宁可打开看一眼。
- `email_check.ignore_senders` 里的发件人跳过。

每封求职邮件提取：公司、岗位、类型（确认收到 / 拒信 / 测评邀请 / 面试邀请 / 进入下一轮 / Offer / 需要操作）、截止日期、需要用户做什么。

## 第 4 步 · 对照投递表并更新

1. `python scripts/check_duplicate.py "<公司>" "<岗位>"` 找到对应编号（邮件没写岗位名就只传公司名）。
   - **只有一条记录对得上**才更新。
   - 对上多条（同公司投过几个岗位，邮件又没写清是哪个）或一条都对不上：**不要猜**，不改投递表，在汇报里列出公司、邮件主题和可能的编号，让用户确认。
2. 按类型更新（只用脚本，不要直接改 Excel）。查邮件的时间范围每次都会和上次重叠，同一封邮件可能看到两次：脚本发现这条已经记过，会输出“已是最新，未改动”，这是正常的。

| 邮件类型 | 命令 |
|---|---|
| 拒信 | `python scripts/update_status.py <编号> --status Rejected --flow "拒 MM-DD"` |
| 在线测评 | `... --status Assessment --flow "OT 截止 MM-DD"` |
| 面试邀请 | `... --status Interview --flow "<轮次> MM-DD"` |
| Offer | `... --status Offer --flow "Offer MM-DD"` |
| 只是确认收到 | 不改状态，可在汇报里一笔带过 |

3. 邮件对应的申请**不在投递表里**（用户自己在别处投的）：只在汇报里提一句，**不要自动新增记录**。
4. 有截止日期的待办：`python scripts/todo.py add "MM-DD 前 <要做的事>（<公司>）"`。它写进 `data/progress.md` 的「待办」段；同样的待办已有就跳过。

## 第 5 步 · 汇报

```
📬 今日邮件汇报（YYYY-MM-DD）
⚠️ <今天或明天截止的事项，放最前面>

有进展的申请：
- 公司 — 岗位 — 状态 — 需要你做的事（截止日期）

待处理：
- 需要回复/操作的邮件（截止日期）

不在投递表里的求职邮件：……（如有）
仍在等待：N 个
```
没有任何求职相关新邮件：只写“今日无新进展”。

## 第 6 步 · 收尾

```bash
python scripts/email_window.py --done
```
只有成功检查完才运行（这样下次会从这里接上）。通知按 `schedule.notify`：`on_change` = 有进展或有截止事项时才发。
