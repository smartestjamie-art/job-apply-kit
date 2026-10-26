# 04 · 周报 / Weekly review

1. 运行 `python scripts/status.py`（各状态数量、近 7 天投递、近 4 周每周投递数、进行中的申请）。
2. 邮件：
   - 已开启每日查邮箱（`config/search.yaml` 的 `schedule.email_check.enabled: true`）：状态已经每天更新，这一步**不再搜邮件**，直接用投递表。
   - 没开启但连接了邮箱：按 `playbooks/07-email-check.md` 第 2–4 步查近 7 天的邮件，**只读不发**。每个更新先列给用户确认，再用 `scripts/update_status.py` 更新。
3. 运行 `python scripts/todo.py list`，列出未来 14 天的待办和截止日期；用户说做完了的用 `python scripts/todo.py done "<关键词>"` 勾掉。
4. 输出：
   - 本周数字（投递数、测评、面试、拒信、Offer）
   - 需要马上处理的事（按截止时间排序）
   - 一两条观察（例如哪个方向回复率高、哪类岗位常被拒），**只基于 tracker 里的真实数据**
5. 在 `data/progress.md` 追加一段 `### 周报 YYYY-MM-DD`。
