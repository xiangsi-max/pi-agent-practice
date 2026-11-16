# 实践课1： Pi Agent安装与使用 luoweicheng

## 基本信息

| 项目 | 内容 |
| --- | --- |
| 姓名拼音 | **luoweicheng** |
| 姓名 | 罗伟城 |
| GitHub 登录名 | [xiangsi-max](https://github.com/xiangsi-max) |

## 仓库地址

https://github.com/xiangsi-max/pi-agent-practice

> 完整报告见该仓库的 [README.md](https://github.com/xiangsi-max/pi-agent-practice/blob/main/README.md)，
> 截图见 [docs/screenshots](https://github.com/xiangsi-max/pi-agent-practice/tree/main/docs/screenshots)，
> 所有终端证据原文见 [docs/logs](https://github.com/xiangsi-max/pi-agent-practice/tree/main/docs/logs)。

## 完成情况总览

| 任务 | 要求 | 状态 | 证据 |
| --- | --- | --- | --- |
| 一 | 本地安装并启动 Pi | ✅ | S1 ｜ `docs/logs/task1-install-and-version.log` |
| 二 | 配置模型 + 最简单会话 | ✅ | S2 ｜ `docs/logs/task2-model-and-session.log` |
| 三 | 切换模型 + 思考级别 | ✅ | S3 ｜ `docs/logs/task3-model-and-thinking.log` |
| 四 | @ 引用代码 + 粘贴小图片 | ✅ | S4、**S5a/S5b（Alt+V 粘贴）**、S5 ｜ `docs/logs/task4a-*.log`、`task4b-*.log`、`tui-task4b-clipboard-*.raw.txt` |
| 五 | 安装并试用一个插件 | ✅ | S6、**S6b（加载）** ｜ `docs/logs/task5-*.log` |
| 六 | PPT Skill（选做） | ✅ 已完成 | S7、S8、**S8b（发现）** ｜ `docs/logs/task6-skill.log`（含源 commit） |

## 环境信息

- 操作系统：Windows（PowerShell）
- Node.js：v26.13.1 ／ npm：11.20.0
- **Pi：1.5.2**（安装路径 `C:\Users\20349\.pi\agent\bin\pi.cmd`）
- 模型提供商：
  - DeepSeek（`deepseek-flash`、`deepseek-v4-pro`）——任务一至三及任务五、六使用
  - `qwen-token-plan-cn`（`deepseek-v4.1-flash`，支持图片输入）——任务四 B 的视觉测试使用，
    因 DeepSeek provider 下的 `deepseek-v4-pro` 的 `images` 为 `no`
  - 该 provider 通过 `~\.pi\agent\models.json` 仅覆盖 `baseUrl` 指向兼容端点，
    模型清单与认证方式不变；该文件含 provider 地址、**不含任何密钥**，故未收入仓库

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

思考级别切换（证据取自 Pi 会话文件 `~\.pi\agent\sessions\<项目>\*.jsonl` 中的
`thinking_level_change` 条目与 assistant 消息的 `thinkingLevel` 字段，不是只看回复文本）：

```text
请求级别   Pi记录级别   模型
off        off          deepseek-flash
low        low          deepseek-flash
high       high         deepseek-flash
```

请求值与 Pi 实际记录值三者一致，说明切换确实生效。

> 踩坑：本想让 `pi --mode json` 直接回写 `thinkingLevel`，但 `message_end.message` 里并没有该字段，
> 读到的永远是空值；真正的落点在会话文件里。验证手段本身也要先验证。

**选择说明**：简单问题（解释名词、算术）用 `deepseek-flash` + `off/low`，快且省；
多文件重构、复杂排错用 `deepseek-v4-pro` + `high`，推理链更长。但高思考级别不保证答案更好，
会增加等待与用量，故日常默认 `medium`。模型切换前后各发同一问题「请用一句话解释持续集成」，
两次均正常返回，确认切换真实生效。

### 任务四 引用代码并粘贴小图片

**A. @ 引用代码文件**：`pi --print "@hello.py" "请解释 @hello.py 的功能……"`，
模型正确解释 `add` 函数并给出输出 `5`，且未修改文件；实际运行 `python hello.py` 输出 `5`，一致。

> 踩坑：`@文件` 必须作为独立参数，与提示词写在同一字符串里会报 `File not found`。

**B. 粘贴小图片**：自制 200×200 蓝色方块 + 白色数字 `7`。按作业要求把**图片内容**放入剪贴板
（`Clipboard.SetImage`，不是复制文件路径），在 Pi 输入区按 **Alt+V**，输入框随即出现 Pi 生成的
附件路径 `C:\Users\20349\AppData\Local\Temp\pi-clipboard-<uuid>.png`（这就是「已附加图片的提示」，见 S5b），
再补提示词发送，模型先 `read` 该附件再作答，正确识别出「白底 / 深蓝色正方形 / 白色数字 7」（见 S5a）。
另用 `@seven.png` 直接引用做了对照（S5），两条输入路径都验证过。
输入原图见仓库 `pi-test/seven.png`，可对照核对识别结果。

### 任务五 安装并试用插件

- 名称：**pi-web-access**（来源 https://pi.dev/packages ）
- 安装：`pi install npm:pi-web-access` → `added 211 packages`、`Installed npm:pi-web-access`
- 加载：**重启后 Pi 启动界面的 `[Extensions]` 区域出现 `npm:pi-web-access`**（见 S6b 真实 TUI 截图），
  工具清单中新增 `web_search`、`source_check`、`fetch_content`、`get_search_content`
- 试用：提示「请获取 https://example.com 的页面标题」，Pi 调用 `fetch_content`，返回 **Example Domain**

### 任务六 PPT Skill（选做，已完成）

- **源 commit（作业要求记录）**：`anthropics/skills` 的 `main` 分支
  **`1780c5e5a552fd4d1c9d6a7b0cab26b0c2bef064`**（`2026-11-14T15:16:42Z`，
  `Update docx, pptx, xlsx, and pdf skills (#2217)`），子目录 `skills/pptx`
- 安装到 `D:\Github course\study\.pi\skills\pptx`，共 **58 个文件**，保留
  `SKILL.md`、`LICENSE.txt` 与 `scripts/`
- 已用 Git blob SHA-1 逐文件比对：本地 58 个文件与该 commit 的 58 个 blob 全部一致。
  作业示例记录的 `2c5958ecac7cee2b583967a2c4981d0f4a75c579`（56 个文件）是同一目录的较早版本，
  本机装的是更新的 main，故此处如实记录 main 的 SHA
- 重启后在启动界面 `[Skills]` 区域的 `project` 分组下出现
  `D:\Github course\study\.pi\skills\pptx\SKILL.md`（见 S8b 真实 TUI 截图）
- 在 `study` 目录执行 `/skill:pptx 请说明这个 Skill 的名称、用途和所在目录，`
  → 正确返回名称 `pptx`、用途及路径 `D:\Github course\study\.pi\skills\pptx\`
- 补齐依赖（`pptxgenjs`、`python-pptx`）后生成两页 PPT，Skill 自带 `validate.py` 校验
  `All validations PASSED!`，并用 PowerPoint 实际打开、导出两页图片确认可正常显示

### 关于截图

S1–S8 由 `tools/render-screenshots.py` 渲染 `docs/logs/` 中的真实终端日志生成，
每张图页脚标注来源日志文件，可逐条回查；S6b、S8b 是 Pi 的**真实 TUI 画面**
（`pywinpty` 开伪终端运行 `pi --verbose`，`pyte` 重建屏幕），原始字节流存于
`docs/logs/tui-capture-*.raw.txt`。

S5a、S5b 同样是**真实 TUI 画面**（`tools/tui-paste.py` 把图片放进剪贴板后按 Alt+V 捕获），
分别对应「已附加图片的提示（未发送）」与「发送后的完整回复」，原始字节流存于
`docs/logs/tui-task4b-clipboard-*.raw.txt`。

> 说明：Pi 只在 TTY 下绘制界面，管道里执行 `pi --verbose` 输出 0 字节，
> 因此「插件/Skill 是否真的加载」必须从真实伪终端的启动界面读取，不能靠安装命令的输出来代替。

## 未提交的敏感信息

- 未提交 `auth.json`
- 未提交任何 API Key、授权回调链接
- 报告中密钥一律以 `<你的密钥>` 占位
