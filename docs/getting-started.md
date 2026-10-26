# 环境准备 / Environment setup

## 必需
- **Claude**：Claude Code（推荐给会用终端的人）或 Claude 桌面端（Cowork）。
- **Python 3.9+**：`python3 --version` 检查。然后在仓库目录运行 `pip install -r requirements.txt`。
  - macOS 没有 Python：安装 https://www.python.org/downloads/ 或 `brew install python`。
  - 不想装 Python：在 Cowork 里，Claude 可以在云端工作区运行脚本，再把结果写回你的文件夹。

## 网页填表（推荐）
- 在 Chrome 安装 **Claude in Chrome** 扩展，并在扩展设置里允许它访问招聘网站。
- 开始投递前先在 Chrome 里登录需要登录的招聘网站（Workday 账号、学校 Careers 等）。

## Claude 桌面端 / Cowork
1. 下载并解压仓库。
2. 在桌面端选择「连接文件夹」，选中 `job-apply-kit` 文件夹。
3. 新建对话，说：“请读 CLAUDE.md，带我开始设置。”

## Claude Code
```bash
git clone https://github.com/smartestjamie-art/job-apply-kit.git
cd job-apply-kit && pip install -r requirements.txt && claude
```
然后输入 `/setup`。`CLAUDE.md` 会被自动读取。

## 验证安装
```bash
python scripts/status.py --setup-check
```
