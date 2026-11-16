"""Capture Pi's real TUI for the clipboard-paste (Alt+V) evidence: S5a / S5b.

Why this exists
---------------
The assignment asks for the clipboard route, not the `@file` route:
"先截取图片内容到剪贴板，不要只复制图片文件的路径" and
"确认出现图片附件或图片输入提示".

Pi only paints its UI on a real TTY (piping `pi --verbose` yields 0 bytes), so we
spawn Pi inside a ConPTY (winpty), put the *bitmap* of a PNG onto the Windows
clipboard (Clipboard.SetImage, NOT a path string), press Alt+V, and rebuild the
screen from the captured escape stream with pyte.

What Pi does with a clipboard image
-----------------------------------
`interactive-mode.js` -> `handleClipboardPaste()`: if the clipboard holds a file
path it inserts that path; else if it holds an image it writes the bytes to
`os.tmpdir()/pi-clipboard-<uuid>.png` and inserts *that* path into the editor.
So the appearance of `pi-clipboard-<uuid>.png` in the input box IS Pi's own
"image attached" indicator — that is the S5b frame.

Usage
-----
    python tui-paste.py <cwd> <png> <out-prefix> <model> [attach|full]

    attach : paste + type prompt, do NOT send  -> S5b
    full   : paste + type prompt + Enter        -> S5a (includes model reply)

Outputs `<out-prefix>-raw.txt` (raw bytes with escapes) and `<out-prefix>.txt`
(clean screen text). Render to PNG with `tools/render-tui.py`.
"""
import os
import queue
import re
import subprocess
import sys
import threading
import time

from winpty import PtyProcess

PI = os.path.join(os.path.expanduser("~"), ".pi", "agent", "bin", "pi.cmd")
PROMPT = "请描述图片中的颜色、形状和数字。"


def strip_ansi(text: str) -> str:
    """Drop CSI / OSC escape sequences so the stream is greppable."""
    text = re.sub(r"\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)", "", text)
    text = re.sub(r"\x1b\[[0-9;?]*[ -/]*[@-~]", "", text)
    text = re.sub(r"\x1b[@-Z\\-_]", "", text)
    return text


def put_image_on_clipboard(png: str) -> str:
    """Put the actual bitmap on the clipboard (GraphicsContext needs STA)."""
    script = (
        "Add-Type -AssemblyName System.Windows.Forms;"
        "Add-Type -AssemblyName System.Drawing;"
        f"$img=[System.Drawing.Image]::FromFile('{os.path.abspath(png)}');"
        "[System.Windows.Forms.Clipboard]::SetImage($img);"
        "$img.Dispose();"
        "Write-Output ('clipboard ' + [System.Windows.Forms.Clipboard]::ContainsImage())"
    )
    r = subprocess.run(["powershell", "-STA", "-NoProfile", "-Command", script],
                       capture_output=True, text=True)
    return r.stdout.strip()


def capture(cwd: str, png: str, out_prefix: str, model: str,
            mode: str = "full", cols: int = 150, rows: int = 48) -> None:
    print("clipboard:", put_image_on_clipboard(png))

    env = dict(os.environ)
    env["TERM"] = "xterm-256color"
    env["PYTHONIOENCODING"] = "utf-8"
    # NOTE: do NOT pass --verbose here; the startup help fills the screen and
    # covers the input box, which is exactly what we need to see.
    p = PtyProcess.spawn([PI, "--model", model], cwd=cwd, env=env,
                         dimensions=(rows, cols))

    q, stop = queue.Queue(), threading.Event()

    def reader():
        # PtyProcess.read() blocks when idle, so read on a daemon thread and
        # let the main thread keep control of the timing.
        while not stop.is_set():
            try:
                data = p.read(8192)
            except Exception:
                break
            if data:
                q.put(data)
            else:
                time.sleep(0.05)

    threading.Thread(target=reader, daemon=True).start()

    steps = [(14.0, "\x1bv", "Alt+V (paste clipboard image)"),
             (18.0, PROMPT, "typed prompt")]
    if mode == "full":
        steps.append((21.0, "\r", "Enter (send)"))

    total = 100 if mode == "full" else 30
    start, idx = time.time(), 0
    while time.time() - start < total:
        t = time.time() - start
        if idx < len(steps) and t > steps[idx][0]:
            try:
                p.write(steps[idx][1])
            except Exception:
                pass
            print(f"  {steps[idx][2]} at {t:.1f}s")
            idx += 1
        time.sleep(0.1)

    stop.set()
    time.sleep(0.3)
    try:
        p.terminate(force=True)
    except Exception:
        pass

    chunks = []
    while not q.empty():
        chunks.append(q.get())
    raw = "".join(chunks)

    raw_path = out_prefix + "-raw.txt"
    clean_path = out_prefix + ".txt"
    with open(raw_path, "w", encoding="utf-8", errors="replace") as fh:
        fh.write(raw)
    clean = strip_ansi(raw)
    with open(clean_path, "w", encoding="utf-8", errors="replace") as fh:
        fh.write(clean)

    print(f"raw={len(raw)} clean={len(clean)} -> {raw_path}")
    for kw in ["pi-clipboard", "read ", "图片描述"]:
        print(f"  {kw!r}: {clean.count(kw)}")


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print(__doc__)
        sys.exit(1)
    capture(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4],
            sys.argv[5] if len(sys.argv) > 5 else "full")
