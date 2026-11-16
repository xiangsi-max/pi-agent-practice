"""Capture the real Pi TUI screen from a pseudo-console (ConPTY via winpty).

Why this exists: pi renders its interactive UI only to a TTY. Piping stdin in
gives 0 bytes -- `pi --verbose | Out-String` proves nothing. winpty provides a
real pseudoconsole so we can read the bytes Pi actually draws.

`PtyProcess.read()` blocks when the TUI is idle, so all reading happens on a
daemon thread that feeds a queue; the main thread owns the timing (when to type
keys, when to stop).

Usage:
  python tui_capture.py <cwd> <out-raw> <out-clean> [seconds] [keys]
  keys are '||'-separated, with \\r for Enter, e.g. "/skills\r"
"""
import os
import queue
import re
import sys
import threading
import time

from winpty import PtyProcess

PI = r"C:\Users\20349\.pi\agent\bin\pi.cmd"


def strip_ansi(text: str) -> str:
    text = re.sub(r"\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)", "", text)
    text = re.sub(r"\x1b\[[0-9;?]*[ -/]*[@-~]", "", text)
    text = re.sub(r"\x1b[@-Z\\-_]", "", text)
    return text


def capture(cwd, total_seconds=45, cols=150, rows=48, keys=None,
            settle_seconds=20):
    env = dict(os.environ)
    env["TERM"] = "xterm-256color"
    env["PYTHONIOENCODING"] = "utf-8"

    p = PtyProcess.spawn([PI, "--verbose"], cwd=cwd, env=env,
                         dimensions=(rows, cols))

    q = queue.Queue()
    stop = threading.Event()

    def reader():
        while not stop.is_set():
            try:
                data = p.read(8192)
            except Exception:
                break
            if data:
                q.put(data)
            else:
                time.sleep(0.05)

    t = threading.Thread(target=reader, daemon=True)
    t.start()

    start = time.time()
    sent = False
    while time.time() - start < total_seconds:
        if keys and not sent and time.time() - start > settle_seconds:
            for k in keys:
                time.sleep(0.7)
                try:
                    p.write(k)
                except Exception:
                    break
            sent = True
        time.sleep(0.1)
        if not p.isalive() and q.empty():
            break

    stop.set()
    time.sleep(0.3)
    try:
        p.terminate(force=True)
    except Exception:
        pass

    chunks = []
    while not q.empty():
        chunks.append(q.get())
    return "".join(chunks)


if __name__ == "__main__":
    cwd = sys.argv[1]
    out_raw = sys.argv[2]
    out_clean = sys.argv[3]
    total = int(sys.argv[4]) if len(sys.argv) > 4 else 45
    keys_arg = sys.argv[5] if len(sys.argv) > 5 else ""

    keys = None
    if keys_arg:
        keys = [k.replace("\\r", "\r") for k in keys_arg.split("||")]

    raw = capture(cwd, total_seconds=total, keys=keys)
    clean = strip_ansi(raw)
    with open(out_raw, "w", encoding="utf-8", errors="replace") as f:
        f.write(raw)
    with open(out_clean, "w", encoding="utf-8", errors="replace") as f:
        f.write(clean)
    print(f"cwd={cwd} raw={len(raw)} clean={len(clean)}")
    for kw in ["Extension", "Skill", "web-access", "pptx", "loaded"]:
        print(f"  {kw!r}: {clean.count(kw)}")
