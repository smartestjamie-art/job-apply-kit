# ATS 踩坑速查 / ATS pitfalls

| 平台 / 场景 | 坑 | 应对 |
|---|---|---|
| **Workday** | 自定义搜索下拉（Field of Study、Ethnicity 等）打字不过滤；点 checkbox/radio 图标常不生效 | 手动滚动列表，点**文字 label**；每次点完截图确认 |
| Workday「Autofill with Resume」 | 法定名被填成常用名；Role Description 混入后面章节；一条项目被拆成空白的假 Work Experience | 手动改 Legal/Preferred Name 两个分区；逐条核对描述（ctrl+a 常选不全，用 form_input 整段覆盖）；删除假条目并反复检查 |
| Workday 电话 | Phone Number 与 Country Phone Code 重复带国家码，或带前导 0 | 区号单独一栏时号码栏只填本地号码（无 0、无国家码） |
| Workday 最后一步泛化 Page Error | 刷新会被强制登出，看起来数据全丢 | 重新登录后检查：通常只有报错那一步被清空，前面步骤服务器端已保存 |
| **Taleo（tal.net）** | 页面用隐藏的原生 `<select>` + “chosen” 控件，搜索框不过滤；后退/刷新会 “Duplicate form submission” 并登出 | 用 JS：`s.selectedIndex=i; s.dispatchEvent(new Event('change',{bubbles:true})); jQuery(s).trigger('change').trigger('chosen:updated')`；不要用后退/刷新；Cover Letter 可能是必填 |
| Taleo 输出被拦截 | javascript 返回含 `=`/`?`/`&` 的内容时可能显示 “[BLOCKED: Cookie/query string data]” | 只输出纯文字，去掉这些字符再打印 |
| **Ashby** | Name/Email 用 form_input 只改 DOM，React 收不到值，提交报 “Missing entry for required field” | 用键盘输入（triple_click → Delete → type）；Yes/No 按钮用点击；下拉先点开、输入首字母、再点选项；file_upload 对 Resume 的 file input ref 有效 |
| **SmartRecruiters** | 简历上传框在 shadow DOM，自动上传工具拿不到 | 请用户自己点 Choose a file；下拉先点开再点选项 |
| **Oracle 招聘表单** | 下拉要先点开再输入再点选项 | 逐步操作并截图确认 |
| **Google Forms（自建）** | 文件上传是跨域 iframe + 原生 Drive 选择器，无法自动化；表单会记录登录的 Google 账号 | 文字照填；上传由用户完成；提交前提醒确认账号身份 |
| **自建 ATS 的 Resume Autofill** | 项目名被当成当前雇主；技术名词（ResNet、6G…）被当成公司，生成多条假雇主 | 上传后完整核对 Personal Information 与 Work History，删假条目，只保留真实经历 |
| **同源 iframe 里的 file input** | 无障碍树不穿透 iframe，`file_upload` 用不了 | 不要反复点 Browse；若有 “paste your CV” 文本框改用它；否则请用户上传 |
| **CKEditor / 富文本** | form_input 报成功但编辑器实际仍空（未触发真实交互） | 点击编辑区后用键盘输入；一定截图验证 |
| **意外提交** | 填到最后一两个字段时 form_input/find 连续报 stale reference 并重试，有小概率页面自行跳到成功页 | 先截图确认页面状态，不要连续重试；若已提交，如实告诉用户并记录 |
| **Apply by email** | JD 只写发邮件 | 只建草稿，用户自己加附件并发送 |
| **雇主禁止 AI 作答** | 部分律所/专利岗位在 JD 声明 | 开放题只写占位草稿，由用户重写 |
| **登录会话** | 账号会话中途失效 | 请用户重新登录；登录后检查已填步骤是否还在 |
| **Cookie 弹窗** | — | 默认拒绝非必要 Cookie |
| **截图延迟** | 截图常落后一步 | 操作后再截一次图；页面滚动会让坐标偏移，改用 ref 点击 |
