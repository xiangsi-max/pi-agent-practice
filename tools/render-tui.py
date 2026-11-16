"""Render a captured PTY byte stream into a PNG of the terminal screen.

The raw stream from tui_capture.py is a series of escape sequences. Feeding it
into pyte (a terminal emulator) reproduces the final visible screen, which we
then draw with Pillow using a CJK-capable font.
"""
import sys

import pyte
from PIL import Image, ImageDraw, ImageFont

COLS, ROWS = 150, 48
COLS_WIDTH_RATIO = 0.6


def screen_from_raw(raw: str, cols=COLS, rows=ROWS):
    screen = pyte.Screen(cols, rows)
    stream = pyte.Stream(screen)
    stream.feed(raw)
    return screen


def render(screen, out_path, cols=COLS, rows=ROWS, title=None):
    # Consolas for ASCII (fixed advance matches the 8px cell), Microsoft YaHei
    # for CJK (double-width cell). Mixing keeps the grid aligned.
    ascii_font = ImageFont.truetype(r"C:\Windows\Fonts\consola.ttf", 14)
    cjk_font = ImageFont.truetype(r"C:\Windows\Fonts\msyh.ttc", 13)
    font_path = r"C:\Windows\Fonts\msyh.ttc"
    cell_w = 8
    cell_h = 17
    font = ascii_font

    pad = 16
    header_h = 30 if title else 0
    w = cols * cell_w + pad * 2
    h = rows * cell_h + pad * 2 + header_h

    img = Image.new("RGB", (w, h), (18, 20, 24))
    d = ImageDraw.Draw(img)

    if title:
        d.rectangle([0, 0, w, header_h], fill=(38, 42, 50))
        d.text((pad, 7), title, font=ImageFont.truetype(font_path, 14),
               fill=(210, 215, 225))

    for y in range(rows):
        line = screen.display[y]
        for x, ch in enumerate(line[:cols]):
            if ch.strip() == "":
                continue
            attr = screen.buffer[y][x]
            fg = attr.fg or "default"
            bold = attr.bold
            color = {
                "default": (200, 205, 212),
                "white": (240, 240, 240),
                "black": (90, 95, 105),
                "red": (230, 110, 110),
                "green": (130, 200, 130),
                "blue": (110, 160, 235),
                "yellow": (225, 200, 120),
                "cyan": (120, 205, 210),
                "magenta": (200, 140, 210),
                "brown": (200, 170, 120),
            }.get(fg, (200, 205, 212))
            if bold:
                color = tuple(min(255, c + 35) for c in color)
            use = cjk_font if ord(ch) > 0x2E80 else ascii_font
            d.text((pad + x * cell_w, pad + header_h + y * cell_h),
                   ch, font=use, fill=color)

    img.save(out_path, "PNG")
    return out_path, img.size


if __name__ == "__main__":
    raw_path, out_path = sys.argv[1], sys.argv[2]
    title = sys.argv[3] if len(sys.argv) > 3 else None
    cols = int(sys.argv[4]) if len(sys.argv) > 4 else COLS
    rows = int(sys.argv[5]) if len(sys.argv) > 5 else ROWS

    with open(raw_path, encoding="utf-8", errors="replace") as f:
        raw = f.read()

    screen = screen_from_raw(raw, cols, rows)
    path, size = render(screen, out_path, cols, rows, title)
    print(f"wrote {path} {size}")

    # print non-empty rows so the content is verifiable
    for i, line in enumerate(screen.display):
        if line.strip():
            print(f"{i:>2}|{line.rstrip()}")
