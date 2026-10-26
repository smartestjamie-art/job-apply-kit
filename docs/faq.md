# 常见问题 / FAQ

**Q：我的资料会被上传到 GitHub 吗？**
不会。`profile/profile.yaml`、`cv/`、`data/` 都在 `.gitignore` 里。提交前可以用 `git status` 确认没有这些文件。

**Q：Claude 能替我点提交吗？**
不能，这是硬规则。Claude 填到最后一步，你检查后自己提交，再说“提交了”。

**Q：网站要登录怎么办？**
你自己在 Chrome 里登录，然后告诉 Claude 继续。Claude 不会输入密码，也不会替你注册账号。

**Q：简历上传失败？**
有些系统的上传框在 iframe 或 shadow DOM 里，自动化工具拿不到。Claude 会提示你自己点一次上传，其余字段它继续填。

**Q：页面填着填着把我登出了？**
很多系统会保留已保存的步骤。重新登录后先检查前面的页面，只补被清空的那一页。不要用浏览器后退/刷新（Taleo 等会报重复提交并登出）。

**Q：下拉框里没有我的专业/学校？**
在 profile 的 `subject_fallback` 里设一个备选；学校找不到时 Claude 会选最接近的并在汇报里告诉你。

**Q：签证/担保题怎么答？**
在 `preferences.sponsorship_*` 设定策略，`ask_me` 表示每次留给你。如实作答是你本人的责任，见 `docs/diversity-and-visa.md`。

**Q：多样性问卷能不能都不答？**
可以，把 `preferences.diversity_policy` 设为 `prefer_not_to_say_all`。

**Q：我想投的岗位要求的毕业年份和我不一样？**
Claude 会在打分时标出来，由你决定投不投。

**Q：投递表的数字不对 / 想手动改？**
直接在 Excel 里改即可（Status 列有下拉选项）。改完不用通知 Claude，脚本每次都会重新读取。

**Q：换了一台电脑？**
复制 `profile/profile.yaml`、`cv/`、`data/` 三个位置到新电脑的仓库里即可。

**Q：怎么更新到仓库的新版本？**
`git pull`。你的私人文件不受影响。如果模板新增了字段，Claude 会在校验时提示你补充。
