# -*- coding: utf-8 -*-
"""
把 docs/logs/ 下真实采集到的终端日志渲染成 S1–S8 截图（PNG）。

用途：作业要求提交 S1–S8 截图。本脚本不伪造任何内容，
它只是把 capture-evidence.ps1 实际采集到的终端输出排版成图片。
每张图顶部的标题栏与底部注脚都写明来源日志文件，便于核对。

字体策略：模拟终端等宽栅格。
  - ASCII 字符占 1 格，用 Consolas（等宽）
  - 中日韩字符占 2 格，用微软雅黑，必要时横向压缩以塞进 2 格
这样日志里用空格对齐的表格在图片里也能对齐。
"""

import os
import re
from PIL import Image, ImageDraw, ImageFont

BASE = r"D:\Github course"
LOGS = os.path.join(BASE, "docs", "logs")
OUT = os.path.join(BASE, "docs", "screenshots")
os.makedirs(OUT, exist_ok=True)

# ---------- 主题 ----------
BG = (24, 26, 32)
BG_HEAD = (32, 35, 44)
BG_FOOT = (32, 35, 44)
FG = (222, 226, 232)
FG_DIM = (140, 148, 160)
FG_PROMPT = (106, 190, 120)
FG_HEAD = (120, 180, 255)
FG_CMD = (240, 200, 110)
ACCENT = (0, 102, 204)

FS = 15
LINE_H = 25
PAD_X = 26
PAD_Y = 22
HEAD_H = 46
FOOT_H = 34

CONS = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", FS)
CONS_B = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", FS)
CJK = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", FS)
CJK_B = ImageFont.truetype("C:/Windows/Fonts/msyhbd.ttc", FS)

CELL = CONS.getlength("M")          # 一格的宽度
assert CELL > 0

def is_wide(ch):
    o = ord(ch)
    return (0x1100 <= o <= 0x115F or 0x2E80 <= o <= 0xA4CF or
            0xAC00 <= o <= 0xD7A3 or 0xF900 <= o <= 0xFAFF or
            0xFE30 <= o <= 0xFE6F or 0xFF00 <= o <= 0xFF60 or
            0xFFE0 <= o <= 0xFFE6 or 0x20000 <= o <= 0x3FFFD)

def cells(s):
    return sum(2 if is_wide(c) else 1 for c in s)

def draw_line(d, x, y, s, color, bold=False):
    """逐字符绘制，ASCII 1 格、CJK 2 格，保证空格对齐。"""
    cx = x
    for ch in s:
        if ch == "\t":
            cx += CELL * 4
            continue
        if ch == " ":
            cx += CELL
            continue
        wide = is_wide(ch)
        span = CELL * (2 if wide else 1)
        f = (CJK_B if bold else CJK) if wide else (CONS_B if bold else CONS)
        w = f.getlength(ch)
        if wide and w > span:               # 压缩宽字符塞进 2 格
            f = ImageFont.truetype(f.path, max(8, int(FS * span / w)))
            w = f.getlength(ch)
        d.text((cx, y), ch, font=f, fill=color)
        cx += span
    return cx

def classify(line):
    t = line.rstrip()
    if not t:
        return FG, False
    if t.startswith("## "):
        return FG_HEAD, True
    if re.match(r"^(\$|PS |>|C:\\|D:\\)", t):
        return FG_CMD, False
    if t.startswith(("请求", "安装命令", "安装路径")):
        return FG_CMD, False
    return FG, False

def render(name, title, subtitle, log_text, footer=None):
    lines = log_text.replace("\r\n", "\n").split("\n")
    # 去掉尾部空行
    while lines and not lines[-1].strip():
        lines.pop()
    if not lines:
        lines = ["(日志为空)"]

    widest = max(cells(l) for l in lines)
    widest = max(widest, cells(title), cells(subtitle))
    W = int(PAD_X * 2 + widest * CELL) + 8
    W = min(max(W, 900), 2200)
    H = int(HEAD_H + PAD_Y * 2 + len(lines) * LINE_H + FOOT_H)

    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # 标题栏
    d.rectangle([0, 0, W, HEAD_H], fill=BG_HEAD)
    d.rectangle([0, HEAD_H - 2, W, HEAD_H], fill=ACCENT)
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse([18 + i * 22, 16, 30 + i * 22, 28], fill=c)
    d.text((88, 12), title, font=CJK_B, fill=FG)
    tw = CJK_B.getlength(title)
    d.text((88 + tw + 14, 15), subtitle, font=CJK, fill=FG_DIM)

    # 正文
    y = HEAD_H + PAD_Y
    for line in lines:
        color, bold = classify(line)
        draw_line(d, PAD_X, y, line, color, bold)
        y += LINE_H

    # 页脚
    fy = H - FOOT_H
    d.rectangle([0, fy, W, H], fill=BG_FOOT)
    foot = footer or "数据来源：docs/logs/ —— 由 tools/capture-evidence.ps1 在真实终端中采集"
    d.text((PAD_X, fy + 9), foot, font=CJK, fill=FG_DIM)

    path = os.path.join(OUT, name)
    img.save(path, "PNG")
    print(f"{name}  {W}x{H}  {os.path.getsize(path)} bytes  <- {len(lines)} lines")
    return path

def read_log(fn):
    with open(os.path.join(LOGS, fn), encoding="utf-8") as f:
        return f.read()

def section(text, start_marker):
    """取从 start_marker 开始到结尾的片段。"""
    i = text.find(start_marker)
    if i < 0:
        return "(未找到片段: %s)" % start_marker
    return text[i:]

def section_until(text, start_marker, end_marker):
    i = text.find(start_marker)
    if i < 0:
        return "(未找到片段: %s)" % start_marker
    j = text.find(end_marker, i + len(start_marker))
    return text[i:] if j < 0 else text[i:j]

t1 = read_log("task1-install-and-version.log")
t2 = read_log("task2-model-and-session.log")
t3 = read_log("task3-model-and-thinking.log")
t4a = read_log("task4a-at-file-reference.log")
t4b = read_log("task4b-image-input.log")
t5 = read_log("task5-plugin.log")
t5x = read_log("task5-extension-loaded.log")
t6 = read_log("task6-skill.log")

render("S1-安装与启动.png", "S1", "任务一 · 本地安装并启动 Pi",
       t1, "来源：docs/logs/task1-install-and-version.log")

render("S2-配置模型与会话.png", "S2", "任务二 · 配置模型并完成一次会话",
       t2, "来源：docs/logs/task2-model-and-session.log　密钥未出现在任何截图中")

render("S3-模型与思考级别切换.png", "S3", "任务三 · 切换模型与思考级别（含实际生效值佐证）",
       t3, "来源：docs/logs/task3-model-and-thinking.log")

render("S4-引用代码文件.png", "S4", "任务四 A · @ 引用 hello.py 并解释",
       t4a, "来源：docs/logs/task4a-at-file-reference.log")

# S5 图片任务：去掉 Format-List 里的空行噪声
t4b_clean = "\n".join(l for l in t4b.replace("\r\n", "\n").split("\n")
                      if not (l.strip() == "" or re.match(r"^\s*$", l)))
render("S5-粘贴图片识别.png", "S5", "任务四 B · 粘贴图片并识别（seven.png 见 README 原图）",
       t4b_clean, "来源：docs/logs/task4b-image-input.log")

s6 = t5.rstrip() + "\n\n" + t5x.lstrip()
render("S6-插件安装与试用.png", "S6", "任务五 · 安装并使用 pi-web-access",
       s6, "来源：docs/logs/task5-plugin.log + task5-extension-loaded.log")

render("S7-Skill目录结构.png", "S7", "任务六 · pptx Skill 安装到项目目录",
       section_until(t6, "## 当前项目目录", "## 显式调用 Skill"),
       "来源：docs/logs/task6-skill.log")

render("S8-Skill调用回复.png", "S8", "任务六 · /skill:pptx 显式调用与回复",
       section(t6, "## 显式调用 Skill"),
       "来源：docs/logs/task6-skill.log")

print("\nall screenshots written to", OUT)
