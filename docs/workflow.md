# 整体流程 / Overall flow

```
          ┌──────────── 第一次 ────────────┐
          │ 00-onboarding：读简历 → 访谈     │
          │ → profile.yaml → 校验 → data/   │
          └───────────────┬────────────────┘
                          ▼
  03-find-jobs ──► 岗位链接 ──► 01-apply ──► 你本人提交 ──► 02-log-submission
  （可选）                      查重/打分/选简历/            tracker + JD 存档 + progress
                               求职信/填表（停在提交前）
                          ▼
          测评/面试邀请 ──► update_status.py ──► 05-interview-prep
                          ▼
                 每周 04-weekly-review
```

各步骤的细节都在 `playbooks/` 里。Claude 每次新会话都会先读 `CLAUDE.md`，由它决定走哪个手册。
