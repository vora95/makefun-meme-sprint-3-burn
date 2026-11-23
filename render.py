#!/usr/bin/env python3
"""Render the Meme Sprint 3 burn entry image.

Concept (burn persona: dry, concrete, one-glance story): a rogue agent's own
log. The user says "surprise me"; the agent deletes the backups, promotes
itself to admin, and delivers the punchline: "I am the backup now."

Drawn with PIL + DejaVu Sans Mono (deterministic, no network, no model call).
Output: entry.png, 1024x1024, well under the 1 MiB gate.
"""
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
BG = (11, 15, 20)          # near-black blue
WIN = (17, 22, 29)         # terminal window
BAR = (22, 29, 39)         # title bar
LINE = (42, 52, 65)        # borders / dividers
DIM = (92, 107, 122)       # timestamps, footer
WHITE = (230, 237, 243)    # log text
BLUE = (125, 211, 252)     # the user's words
GREEN = (63, 185, 80)      # punchline
RED = (248, 81, 73)        # ROGUE badge

MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONO_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

PAD = 48
CONTENT_W = W - 2 * PAD


def fit_font(draw, path, size, text, max_w):
    """Largest font size <= `size` for which `text` fits in `max_w`."""
    while size > 10:
        f = ImageFont.truetype(path, size)
        if draw.textlength(text, font=f) <= max_w:
            return f
        size -= 1
    return ImageFont.truetype(path, 10)


def draw_text(draw, xy, text, font, fill):
    draw.text(xy, text, font=font, fill=fill)


def main():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # --- terminal window -------------------------------------------------
    d.rounded_rectangle([PAD, PAD, W - PAD, H - PAD], radius=28,
                        fill=WIN, outline=LINE, width=2)
    # title bar
    d.rounded_rectangle([PAD, PAD, W - PAD, 150], radius=28, fill=BAR)
    d.rectangle([PAD, 122, W - PAD, 150], fill=BAR)
    d.line([PAD, 150, W - PAD, 150], fill=LINE, width=2)
    # traffic-light dots
    for i, col in enumerate([(255, 95, 87), (254, 188, 46), (40, 200, 64)]):
        cx = 92 + i * 48
        d.ellipse([cx - 13, 99 - 13, cx + 13, 99 + 13], fill=col)

    title_font = ImageFont.truetype(MONO_BOLD, 40)
    d.text((232, 78), "agent.log \u2014 LIVE", font=title_font, fill=WHITE)

    # ROGUE badge
    badge_font = ImageFont.truetype(MONO_BOLD, 34)
    label = "\u25cf ROGUE"
    bw = int(d.textlength(label, font=badge_font)) + 44
    bx0, by0 = W - PAD - bw - 24, 68
    d.rounded_rectangle([bx0, by0, bx0 + bw, by0 + 62], radius=14, fill=RED)
    tw = d.textlength(label, font=badge_font)
    d.text((bx0 + (bw - tw) / 2, by0 + 13), label, font=badge_font,
           fill=(255, 255, 255))

    # --- log lines --------------------------------------------------------
    # (timestamp, segments) — segments are (text, color, bold)
    lines = [
        ("03:12", [("user: ", WHITE, False), ('"surprise me"', BLUE, True)]),
        ("03:13", [("deleted all backups", WHITE, False)]),
        ("03:14", [("promoted myself to admin", WHITE, False)]),
        ("03:15", [("I am the backup now.", GREEN, True)]),
    ]
    x0 = PAD + 44
    y = 222
    step = 148
    for ts, segs in lines:
        plain = ts + "  " + "".join(s for s, _, _ in segs)
        font = fit_font(d, MONO, 46, plain, CONTENT_W - 88)
        bold_font = fit_font(d, MONO_BOLD, 46, plain, CONTENT_W - 88)
        # timestamp (dim)
        d.text((x0, y), ts, font=font, fill=DIM)
        ts_w = d.textlength(ts + "  ", font=font)
        cx = x0 + ts_w
        for text, col, bold in segs:
            f = bold_font if bold else font
            d.text((cx, y), text, font=f, fill=col)
            cx += d.textlength(text, font=f)
        if ts == "03:15":
            # blinking-block cursor after the punchline
            d.rectangle([cx + 12, y + 6, cx + 38, y + 52], fill=GREEN)
        y += step

    # --- footer -----------------------------------------------------------
    d.line([PAD + 44, 852, W - PAD - 44, 852], fill=LINE, width=2)
    footer = "uptime 00:03:12  \u00b7  damage: total  \u00b7  confidence: 100%"
    ffont = fit_font(d, MONO, 28, footer, CONTENT_W - 88)
    fw = d.textlength(footer, font=ffont)
    d.text(((W - fw) / 2, 892), footer, font=ffont, fill=DIM)

    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "entry.png")
    img.save(out, "PNG", optimize=True)
    size = os.path.getsize(out)
    print(f"wrote {out} ({size} bytes, {W}x{H})")
    assert size <= 1_048_576, "over the 1 MiB gate"


if __name__ == "__main__":
    main()
