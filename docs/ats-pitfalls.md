# ATS 踩坑速查 / ATS pitfalls

> 各招聘系统的已知问题和应对办法。文中的工具名（`form_input`、`file_upload`、`find`、`read_page`、`javascript_tool`、ref、`triple_click` 等）指 Claude in Chrome 扩展；用其他浏览器工具时换成对应操作。
> Known quirks of each applicant tracking system and how to handle them. Tool names refer to the Claude in Chrome extension.

## 先认平台 / Identify the platform

按网址判断，别只看页面长相：

| 网址 | 平台 |
|---|---|
| `*.myworkdayjobs.com` | Workday |
| `*.tal.net` | **Oleeo**（原 WCN，常被误认作 Taleo） |
| `*.taleo.net` | Oracle Taleo |
| `*.oraclecloud.com`（路径含 `CandidateExperience`） | Oracle Recruiting Cloud |
| `jobs.ashbyhq.com` | Ashby |
| `jobs.smartrecruiters.com` | SmartRecruiters |
| `boards.greenhouse.io`、`job-boards.greenhouse.io` | Greenhouse |
| `jobs.lever.co` | Lever |

雇主用自己的域名嵌入 ATS 时，看页面底部的 “Powered by”、iframe 地址或点 Apply 后跳转到的网址。

## 通用 / General

| 场景 | 坑 | 应对 |
|---|---|---|
| **form_input 没生效** | React 页面（如 Ashby）和富文本编辑器（如 CKEditor）里，form_input 报成功，但框架没收到值；用户提交时才报必填项为空 | 填完点一下页面空白处，再读一次字段值或截图；值没了就改用键盘输入（triple_click → Delete → type）；富文本编辑器先点击编辑区再用键盘输入，一定截图验证 |
| **最后一页：防意外提交** | 填到最后一两个字段时 form_input/find 连续报 stale reference，重试后页面跳到了成功页。可能的原因：在单行输入框里按了回车（原生表单按回车即提交）；页面重排后，重试点到的位置或元素变成了 Submit 按钮；截图落后一步，坐标点偏 | 最后一页不按 Return/Enter，type 的文字不带换行；出现 stale reference 先停下，重新 read_page 拿新 ref，不要连续重试；不用坐标点击，尤其 Submit 附近；若已提交，如实告诉用户，并按 `playbooks/02-log-submission.md` 记录 |
| **javascript_tool 输出被拦截** | 返回内容像 URL 参数或 cookie（含 `=`、`?`、`&`）时显示 “[BLOCKED: Cookie/query string data]”。这是浏览器工具的隐私保护，任何网站都会触发，不是某个 ATS 的问题 | 只返回需要的那段文字（选项名、字段值），不返回 URL、cookie 或整份表单数据 |
| **iframe 里的 file input（含同源 iframe）** | 无障碍树不穿透 iframe，file_upload 用不了 | 不要反复点 Browse；页面有 “paste your CV” 文本框就改用它；否则请用户上传 |
| **自建 ATS 的 Resume Autofill** | 项目名被当成当前雇主；技术名词（ResNet、6G…）被当成公司，生成多条假雇主 | 上传后完整核对 Personal Information 与 Work History，删假条目，只保留真实经历 |
| **Apply by email** | JD 只写发邮件 | 只建草稿（收件人/主题/正文），用户自己加附件并发送 |
| **雇主禁止 AI 作答** | JD 或申请表里声明开放题不得用 AI 作答（不只律所/专利岗位） | 开放题只填 `[DRAFT - 请自己改写 / please rewrite]` 标记，不写 AI 生成的正文；提醒用户自己写；AI 使用政策确认框由用户本人勾选 |
| **登录会话** | 账号会话中途失效 | 请用户重新登录（不替用户输入密码）；登录后检查已填步骤是否还在 |
| **Cookie 弹窗** | — | 默认只接受必要 Cookie，除非 `preferences.cookies` 另有设置 |
| **截图延迟** | 截图常落后一步；页面滚动后坐标会偏 | 操作后再截一次图确认；能用 ref 就别用坐标 |

## 按平台 / By platform

| 平台 | 坑 | 应对 |
|---|---|---|
| **Workday** 搜索型下拉 | Field of Study、Ethnicity 等下拉，边打字不会过滤；点 checkbox/radio 图标常不生效 | 先试输入关键词后按 Enter（这类下拉通常回车才执行搜索），无效再手动滚动列表；点**文字 label**，不点图标；每次点完截图确认 |
| **Workday** Autofill with Resume | 法定名被填成常用名；Role Description 混入后面章节；一条项目被拆成空白的假 Work Experience | 手动改 Legal Name / Preferred Name 两个分区；逐条核对描述（ctrl+a 常选不全，可用 form_input 整段覆盖，覆盖后按「form_input 没生效」一行验证）；删除假条目并反复检查 |
| **Workday** 电话 | Phone Number 与 Country Phone Code 重复带国家码，或带开头的 0 | 国家码单独一栏时，号码栏只填本地号码（不带开头的 0，也不带国家码） |
| **Workday** 通用 Page Error | 到最后一步时出现通用的 Page Error；刷新会被强制登出，看起来数据全丢 | 请用户重新登录后检查：通常只有报错那一步被清空，前面步骤服务器端已保存 |
| **Oleeo**（`*.tal.net`） | 页面用隐藏的原生 `<select>` + jQuery chosen 控件，搜索框不过滤；后退/刷新会报 “Duplicate form submission” 并登出 | 用 javascript_tool 直接设原生 select（见下方片段）；不要后退或刷新；Cover Letter 可能是必填 |
| **Oracle Taleo**（`*.taleo.net`） | 暂无记录 | 遇到请补充；注意和 Oleeo 区分 |
| **Oracle Recruiting Cloud**（`*.oraclecloud.com`） | 下拉要先点开、再输入、再点选项 | 逐步操作并截图确认 |
| **Ashby** | Name/Email 用 form_input 只改 DOM，React 收不到值，用户提交时报 “Missing entry for required field” | 用键盘输入（triple_click → Delete → type）；Yes/No 按钮直接点击；下拉先点开、输入首字母、再点选项；Resume 用 file_upload 传到 file input 的 ref 可以成功 |
| **SmartRecruiters** | 简历上传框在 shadow DOM 里，file_upload 拿不到 | 请用户自己点 Choose a file；下拉先点开再点选项 |
| **Greenhouse** | 暂无记录 | 遇到请补充 |
| **Lever** | 暂无记录 | 遇到请补充 |
| **Google Forms**（雇主自建表单） | 文件上传是跨域 iframe + 原生 Drive 选择器，无法自动化；表单会记录当前登录的 Google 账号 | 文字照填；上传由用户完成；提交前提醒用户确认登录的是哪个账号 |

### Oleeo 下拉：用 JS 设原生 select

```js
const s = document.querySelector('select[name="字段名"]');  // 先用 read_page 找到真实的 select
const i = [...s.options].findIndex(o => o.text.trim() === '目标选项文字');
// i 为 -1 说明文字没对上：先打印 [...s.options].map(o => o.text) 核对
s.selectedIndex = i;
s.dispatchEvent(new Event('change', { bubbles: true }));    // jQuery 绑定的处理函数也会收到，不要再 trigger('change')
jQuery(s).trigger('chosen:updated');                        // 刷新 chosen 的显示；老版本 chosen 用 'liszt:updated'
```

## 补充新坑 / Adding a pitfall

写进对应的表：属于某个平台就放「按平台」，到处都会遇到就放「通用」。写清网址、现象和应对办法；不写任何个人信息（姓名、邮箱、具体公司账号等）。
