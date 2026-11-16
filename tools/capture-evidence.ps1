# Evidence capture for Pi Agent practice assignment
# Re-runs every task and records verifiable terminal transcripts.
# The API key is read from $env:DEEPSEEK_API_KEY and is never echoed or written to logs.

$ErrorActionPreference = 'Continue'
$base = 'D:\Github course'
$logs = Join-Path $base 'docs\logs'
New-Item -ItemType Directory -Force -Path $logs | Out-Null
$pi = Join-Path $env:USERPROFILE '.pi\agent\bin\pi.cmd'

function Capture([string]$file, [scriptblock]$body) {
    Write-Host ('===== ' + $file + ' =====')
    $out = & $body 2>&1 | Out-String
    $out | Set-Content -Path (Join-Path $logs $file) -Encoding UTF8
    Write-Host ('  -> saved ' + $file)
}

# ---------- Task 1: installation ----------
Capture 'task1-install-and-version.log' {
    '## Pi 安装与版本'
    '安装命令: powershell -c "irm https://pi.dev/install.ps1 | iex"'
    ('安装路径: ' + $pi)
    ''
    '## pi --version'
    & $pi --version
    ''
    '## 启动工作目录'
    ('Get-Location: ' + (Get-Location).Path)
    ''
    '## 运行时版本'
    ('node ' + (node -v))
    ('npm  ' + (& npm.cmd -v))
}

# ---------- Task 2: model config + session ----------
Set-Location (Join-Path $base 'pi-test')
Capture 'task2-model-and-session.log' {
    '## 可用模型列表 (pi --list-models)'
    & $pi --list-models
    ''
    '## 凭证来源: 环境变量 DEEPSEEK_API_KEY (未写入 auth.json, 未打印)'
    ''
    '## 会话: 提示词 你好'
    & $pi --print '你好'
}

# ---------- Task 3: model switch + thinking level ----------
Capture 'task3-model-and-thinking.log' {
    '## 切换前: deepseek-flash, thinking=medium'
    & $pi --model deepseek/deepseek-flash --print --thinking medium '请用一句话解释持续集成'
    ''
    '## 切换后: deepseek-v4-pro, thinking=medium'
    & $pi --model deepseek/deepseek-v4-pro --print --thinking medium '请用一句话解释持续集成'
    ''
    '## 思考级别 off (deepseek-flash)'
    & $pi --model deepseek/deepseek-flash --print --thinking off '1+1=? 只回答数字'
    ''
    '## 思考级别 high (deepseek-flash)'
    & $pi --model deepseek/deepseek-flash --print --thinking high '1+1=? 只回答数字'
}

# ---------- Task 4A: @ file reference ----------
Capture 'task4a-at-file-reference.log' {
    '## 文件 hello.py 内容'
    Get-Content .\hello.py
    ''
    '## Pi 会话: @hello.py + 提示词'
    & $pi --model deepseek/deepseek-v4-pro --print '@hello.py' '请解释 @hello.py 的功能，说明运行后输出什么。只解释，不修改文件。'
    ''
    '## 文件是否被修改 (应与上面完全一致)'
    Get-Content .\hello.py
    ''
    '## 实际运行输出'
    python .\hello.py
}

# ---------- Task 4B: image input ----------
Capture 'task4b-image-input.log' {
    '## 测试图片 seven.png (200x200, 蓝色方块 + 白色数字 7)'
    (Get-Item .\seven.png | Select-Object Name, Length | Format-List | Out-String)
    ''
    '## Pi 会话: @seven.png + 提示词 (使用支持图片输入的 deepseek-flash)'
    & $pi --model deepseek/deepseek-flash --print '@seven.png' '请描述图片中的颜色、形状和数字。'
}

# ---------- Task 5: plugin ----------
Capture 'task5-plugin.log' {
    '## 安装命令'
    'pi install npm:pi-web-access'
    ''
    '## pi list'
    & $pi list
    ''
    '## 插件功能调用: 获取网页标题'
    & $pi --model deepseek/deepseek-v4-pro --print '请获取 https://example.com 的页面标题'
}

# ---------- Task 6: pptx skill ----------
Set-Location (Join-Path $base 'study')
Capture 'task6-skill.log' {
    '## 当前项目目录'
    (Get-Location).Path
    ''
    '## 目录结构 (.pi\skills\pptx 前两层)'
    $root = (Get-Location).Path + '\'
    Get-ChildItem .\.pi\skills\pptx -Recurse -Depth 1 |
        Select-Object @{n='条目';e={$_.FullName.Replace($root,'')}} |
        Format-Table -AutoSize | Out-String
    ''
    '## 文件总数'
    (Get-ChildItem .\.pi\skills\pptx -Recurse -File | Measure-Object).Count
    ''
    '## 显式调用 Skill'
    & $pi --model deepseek/deepseek-v4-pro --approve --print '/skill:pptx 请说明这个 Skill 的名称、用途和所在目录，'
}

Write-Host ''
Write-Host ('All evidence captured under ' + $logs)
