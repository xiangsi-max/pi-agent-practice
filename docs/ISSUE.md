# 实践课1： Pi Agent安装与使用 xiangsi-max

## 仓库地址

> 把下面这行替换成你 push 后的仓库地址
> `https://github.com/<你的用户名>/<仓库名>`

## 完成情况总览

| 任务 | 要求 | 状态 | 证据 |
| --- | --- | --- | --- |
| 一 | 本地安装并启动 Pi | ✅ | `docs/logs/task1-install-and-version.log` |
| 二 | 配置模型 + 最简单会话 | ✅ | `docs/logs/task2-model-and-session.log` |
| 三 | 切换模型 + 思考级别 | ✅ | `docs/logs/task3-model-and-thinking.log` |
| 四 | @ 引用代码 + 粘贴小图片 | ✅ | `docs/logs/task4a-*.log`、`task4b-*.log` |
| 五 | 安装并试用一个插件 | ✅ | `docs/logs/task5-*.log` |
| 六 | PPT Skill（选做） | ✅ 已完成 | `docs/logs/task6-skill.log` |

## 环境信息

- 操作系统：Windows（PowerShell）
- Node.js：v26.13.1 ／ npm：11.20.0
- **Pi：1.5.2**（安装路径 `C:\Users\20349\.pi\agent\bin\pi.cmd`）
- 模型提供商：DeepSeek（`deepseek-flash`、`deepseek-v4-pro`）

## 各任务说明

### 任务一 安装并启动

```powershell
powershell -c "irm https://pi.dev/install.ps1 | iex"
```

安装完成输出 `Managed Pi install complete`，`pi --version` 返回 `1.5.2`。

> 遇到的问题：本机 PowerShell 执行策略为 `Restricted`，直接运行 `pi` 会提示
> `因为在此系统上禁止运行脚本`。改为调用 `pi.cmd`，或执行
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` 后恢复正常。

### 任务二 配置模型并完成会话

采用 **API Key** 方式，通过环境变量 `DEEPSEEK_API_KEY` 注入，避免密钥写入 `auth.json`。

`pi --list-models` 结果：

```text
provider  model            context  max-out  thinking  images
deepseek  deepseek-flash   1M       384K     yes       yes
deepseek  deepseek-v4-pro  1M       384K     yes       no
```

发送 `你好` 后模型正常回复。

### 任务三 切换模型与思考级别

模型切换（同一问题，切换前后各问一次，均正常回复）：

| 阶段 | 模型 |
| --- | --- |
| 切换前 | `deepseek-flash` |
| 切换后 | `deepseek-v4-pro` |

思考级别切换（用 `--mode json` 读取 Pi 回写的 `thinkingLevel` 字段验证确实生效）：

```text
requested=off   ->  thinkingLevel=off
requested=low   ->  thinkingLevel=low
requested=high  ->  thinkingLevel=high
```

选择理由：简单问题用 `deepseek-flash` + `off/low`（快、省）；多文件重构或复杂排错用
`deepseek-v4-pro` + `high`。但高思考级别不保证答案更好，会增加等待与用量，故日常默认 `medium`。

### 任务四 引用代码并粘贴小图片

**A. @ 引用代码文件**：`pi --print "@hello.py" "请解释 @hello.py 的功能……"`，
模型正确解释 `add` 函数并给出输出 `5`，且未修改文件；实际运行 `python hello.py` 输出 `5`，一致。

> 踩坑：`@文件` 必须作为独立参数，与提示词写在同一字符串里会报 `File not found`。

**B. 粘贴小图片**：自制 200×200 蓝色方块 + 白色数字 `7`，切到支持视觉的 `deepseek-flash`
（`deepseek-v4-pro` 的 `images` 为 `no`），模型正确识别出「白底、蓝色正方形、数字 7」。

### 任务五 安装并试用插件

- 名称：**pi-web-access**（来源 https://pi.dev/packages ）
- 安装：`pi install npm:pi-web-access` → `added 211 packages`、`Installed npm:pi-web-access`
- 加载：重启后工具清单中新增 `web_search`、`source_check`、`fetch_content`、`get_search_content`
- 试用：提示「请获取 https://example.com 的页面标题」，Pi 调用 `fetch_content`，返回 **Example Domain**

### 任务六 PPT Skill（选做，已完成）

- 安装到 `D:\Github course\study\.pi\skills\pptx`，共 **58 个文件**，保留
  `SKILL.md`、`LICENSE.txt` 与 `scripts/`
- 重启后在 `study` 目录执行 `/skill:pptx 请说明这个 Skill 的名称、用途和所在目录，`
  → 正确返回名称 `pptx`、用途及路径 `D:\Github course\study\.pi\skills\pptx\`
- 补齐依赖（`pptxgenjs`、`python-pptx`）后生成两页 PPT，Skill 自带 `validate.py` 校验
  `All validations PASSED!`，并用 PowerPoint 实际打开、导出两页图片确认可正常显示

## 未提交的敏感信息

- 未提交 `auth.json`
- 未提交任何 API Key、授权回调链接
- 报告中密钥一律以 `<你的密钥>` 占位
