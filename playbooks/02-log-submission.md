# 02 · 记录投递 / Log a submission

用户说“提交了”之后**立即**做，三件事一次完成：

```bash
python scripts/log_application.py \
  --title "<岗位>" --company "<公司>" --location "<城市>" \
  --url "<链接>" --source "<发现渠道，例如 LinkedIn / 公司官网 / 学校 Careers>" \
  --fit <分数> --cover <Y/N> --cv "<简历版本，例如 software/Your Name.pdf>" \
  --salary "<薪资，没写就留空>" \
  --notes "<关键信息：表单里的特殊选择、留给用户的项目、后续测评要求>" \
  --jd-file data/tmp_jd.md
```

脚本会：
1. 在 `data/applications.xlsx` 新增一行（自动编号，状态 = Applied），保存后重新读取验证；
2. 把 JD 全文插入 `data/JD_archive.md` 最前面（时间倒序），标题 `## #编号 公司 — 岗位 | 日期`；
3. 在 `data/progress.md` 追加一行进展。

然后：
- 提交成功页如果提到在线测评、视频面试、截止日期 → 用 `python scripts/update_status.py <编号> --status "Assessment 测评中" --flow "OT 截止 MM-DD"` 更新，并在回复里提醒用户。
- 回复用户一句话：“已记录为 #N”，加上下一步待办（如有）。

**Job Source 填发现岗位的渠道，不填招聘系统名称。** Flow 只写关键节点+日期，例如 `OT 10-31→HR 面 11-10`。
