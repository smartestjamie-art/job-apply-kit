# 求职信模板 / Cover letter template

Claude 写求职信时遵守：
- 英文。表单文本框：100–150 词；需要上传 PDF：可到 250–350 词、一页以内。
- **每个事实和数字都必须来自 `profile/profile.yaml`**（projects.metrics、experience.bullets 等）。
- 第一段对应 JD 最关键的要求；中间 1–2 个具体证据；结尾一句具体的公司兴趣（不是套话）。
- 保存为 `data/cover_letters/<公司>_<岗位>.md`；要上传文件时运行
  `python scripts/make_cover_letter_pdf.py data/cover_letters/<文件>.md`（页眉自动取 profile 的姓名和联系方式）。

## 短版（文本框）
```
Dear [Company] team,

I'm applying for the [Role] role. [One sentence linking your strongest, true skill to the most important requirement.]

In [project/experience], I [what you did] — [real result from profile]. [Second relevant point.]

[One specific reason this company/team/product interests you.]

Best regards,
[Name]
```

## 长版（PDF，不写页眉，脚本会加）
```
Dear [Company] Early Careers team,

I am applying for the [Programme/Role] in [City]. I [current status: degree, school, graduation], and I want to [goal that fits the role].

[Paragraph 2: strongest evidence — project or internship, with real numbers from profile.]

[Paragraph 3: second piece of evidence or teamwork/ownership example.]

[Paragraph 4: why this company and this programme, specific.]

Thank you for considering my application. I would be glad to discuss it further.

Yours sincerely,
[Name]
```

## 检查清单
- [ ] 没有 profile 里不存在的数字或经历
- [ ] 公司名、岗位名拼写正确
- [ ] JD 或申请表声明禁止 AI 时：不写求职信正文，只放 `[DRAFT - 请自己改写]` 标记，由本人自己写
