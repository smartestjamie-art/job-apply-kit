# Getting started / 上手

1. 安装 Claude Cowork 或 Claude Code，并在 Chrome 安装 Claude in Chrome 扩展（浏览器自动化需要）。
2. 填写 `profile/profile.yaml`，把 CV 放进 `cv/`。
3. 生成 Tracker：`pip install openpyxl && python tracker/make_tracker.py`
4. 第一次对话示例：
   > 请先读 `CLAUDE.md` 和 `profile/profile.yaml`。然后帮我评估并投递：https://…（填到最后一步停下，我自己提交）
5. 你提交后告诉 Claude “提交了”，它会记录 Tracker / JD 存档 / progress。

## 小贴士
- 需要登录的网站，你先登录，再让 Claude 继续。
- 遇到自动化做不了的上传框，Claude 会提示你手动点一次。
- 每周让 Claude 汇总一次：新增投递数、被拒/测评/面试情况、待办截止日期。
