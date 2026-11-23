#!/usr/bin/env python3
"""Render the front page for Monday 23 November 2026 as a 1024x1024 PNG.

Classic newspaper style: off-white paper, black ink, one red accent.
Run: python3 render_image.py [output_path]   (default: entry.png)
Deterministic: fixed fonts, fixed layout, no timestamps, no randomness.
"""

import sys

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
PAPER = (247, 242, 231)
INK = (18, 18, 18)
RED = (178, 34, 34)
GREY = (90, 84, 74)
MARGIN = 44
CONTENT = W - 2 * MARGIN  # 936

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
SANS_BOLD = FONT_DIR + "DejaVuSans-Bold.ttf"
SERIF = FONT_DIR + "DejaVuSerif.ttf"
SERIF_BOLD = FONT_DIR + "DejaVuSerif-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def text_w(draw, text, fnt):
    return draw.textlength(text, font=fnt)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    words = text.split()
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_w(draw, trial, fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_headline(draw, text, fnt_path, start_size, max_w, max_lines):
    """Shrink headline font until it wraps into at most max_lines lines."""
    size = start_size
    while size > 18:
        fnt = font(fnt_path, size)
        lines = wrap(draw, text, fnt, max_w)
        if len(lines) <= max_lines:
            return fnt, lines
        size -= 2
    fnt = font(fnt_path, size)
    return fnt, wrap(draw, text, fnt, max_w)


MASTHEAD = "THE WORLD IN ONE PICTURE"
DATELINE = "MONDAY  \u2022  23 NOVEMBER 2026"

LEAD = {
    "label": "CLIMATE",
    "headline": "COP31 ENDS WITH NO DEAL",
    "body": (
        "The longest climate summit on record closes in Antalya without a pact, "
        "after the EU and others reject a text that never named fossil fuels. "
        "It is the first such failure since Copenhagen in 2009, and the UN chief "
        "says the science has 'no ambiguity'."
    ),
}

PANELS = [
    {
        "label": "MIDDLE EAST",
        "headline": "BAHRAIN DEMANDS UN ACTION",
        "body": (
            "After Iran's strike on a civilian facility, Bahrain takes its case "
            "to the United Nations, with Saudi Arabia in solidarity. A Houthi "
            "missile aimed at the kingdom is intercepted."
        ),
    },
    {
        "label": "DISASTER",
        "headline": "50 MISSING IN INDONESIA FACTORY FIRE",
        "body": (
            "Rescuers search the ruins of a Cikande candy factory for about 50 "
            "workers still unaccounted for. Seven body bags have been recovered; "
            "some 300 people were on shift when the fire broke out."
        ),
    },
    {
        "label": "WAR",
        "headline": "DRONE LEVELS KYIV APARTMENT BLOCK",
        "body": (
            "A Russian drone collapses part of a five-storey building in Dymer, "
            "north of Kyiv. Fourteen people are unaccounted for as rescuers dig "
            "through the rubble."
        ),
    },
    {
        "label": "ASIA",
        "headline": "SOUTH KOREA MINISTER QUITS OVER AI CHEATING",
        "body": (
            "Education Minister Choi Kyo-jin resigns over an AI-assisted cheating "
            "scandal, days before the Suneung college entrance exam."
        ),
    },
    {
        "label": "DIPLOMACY",
        "headline": "NEPAL'S PM HOLDS TALKS WITH MODI",
        "body": (
            "Balendra Shah's state visit to India closes with talks in New Delhi "
            "reviewing the two neighbours' ties."
        ),
    },
]


def draw_label(draw, x, y, text, size):
    fnt = font(SANS_BOLD, size)
    draw.text((x, y), text, font=fnt, fill=RED)
    return y + size + 6


def draw_panel(draw, x, y, width, story, hl_size, body_size, body_lh):
    """Draw one story panel; returns the y just below it."""
    y = draw_label(draw, x, y, story["label"], 20)
    fnt, lines = fit_headline(draw, story["headline"], SANS_BOLD, hl_size, width, 3)
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=INK)
        y += fnt.size + 2
    y += 2
    bfnt = font(SERIF, body_size)
    for line in wrap(draw, story["body"], bfnt, width):
        draw.text((x, y), line, font=bfnt, fill=INK)
        y += body_lh
    return y


def render(hl_size, body_size, body_lh, lead_body_size):
    """Lay out the whole page; returns (image, total_height)."""
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    # ---- Masthead ----
    size = 74
    while size > 40:
        fnt = font(SANS_BOLD, size)
        if text_w(draw, MASTHEAD, fnt) <= CONTENT:
            break
        size -= 2
    y = 34
    draw.text(((W - text_w(draw, MASTHEAD, fnt)) / 2, y), MASTHEAD,
              font=fnt, fill=INK)
    y += size + 10

    # Dateline with red rules on each side
    dfnt = font(SANS_BOLD, 30)
    dw = text_w(draw, DATELINE, dfnt)
    cx = (W - dw) / 2
    rule_y = y + 15
    draw.line([(MARGIN, rule_y), (cx - 18, rule_y)], fill=RED, width=3)
    draw.line([(cx + dw + 18, rule_y), (W - MARGIN, rule_y)], fill=RED, width=3)
    draw.text((cx, y), DATELINE, font=dfnt, fill=INK)
    y += 30 + 12

    # Double rule under masthead
    draw.line([(MARGIN, y), (W - MARGIN, y)], fill=INK, width=4)
    y += 8
    draw.line([(MARGIN, y), (W - MARGIN, y)], fill=INK, width=2)
    y += 16

    # ---- Lead story, spanning full width ----
    y = draw_label(draw, MARGIN, y, LEAD["label"], 24)
    lfnt, llines = fit_headline(draw, LEAD["headline"], SANS_BOLD, 52, CONTENT, 2)
    for line in llines:
        draw.text((MARGIN, y), line, font=lfnt, fill=INK)
        y += lfnt.size + 4
    y += 4
    lbfnt = font(SERIF, lead_body_size)
    for line in wrap(draw, LEAD["body"], lbfnt, CONTENT):
        draw.text((MARGIN, y), line, font=lbfnt, fill=INK)
        y += lead_body_size + 8
    y += 10

    # Rule above the panels
    draw.line([(MARGIN, y), (W - MARGIN, y)], fill=INK, width=2)
    y += 16
    panels_top = y

    # ---- Two columns: left panels 0,1 ; right panels 2,3,4 ----
    gap = 32
    col_w = (CONTENT - gap) // 2
    left_x = MARGIN
    right_x = MARGIN + col_w + gap

    ly = panels_top
    for i in (0, 1):
        ly = draw_panel(draw, left_x, ly, col_w, PANELS[i],
                        hl_size, body_size, body_lh)
        if i < 1:
            ly += 8
            draw.line([(left_x, ly), (left_x + col_w, ly)], fill=GREY, width=1)
            ly += 12
    ry = panels_top
    for i in (2, 3, 4):
        ry = draw_panel(draw, right_x, ry, col_w, PANELS[i],
                        hl_size, body_size, body_lh)
        if i < 4:
            ry += 8
            draw.line([(right_x, ry), (right_x + col_w, ry)], fill=GREY, width=1)
            ry += 12

    # Vertical divider between columns
    draw.line([(MARGIN + col_w + gap // 2, panels_top),
               (MARGIN + col_w + gap // 2, max(ly, ry))], fill=GREY, width=1)

    bottom = max(ly, ry)
    # Footer rule + date line
    fy = bottom + 12
    draw.line([(MARGIN, fy), (W - MARGIN, fy)], fill=INK, width=2)
    ffnt = font(SANS_BOLD, 18)
    footer = "MONDAY 23 NOVEMBER 2026"
    draw.text(((W - text_w(draw, footer, ffnt)) / 2, fy + 8), footer,
              font=ffnt, fill=GREY)
    return img, fy + 8 + 18


def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    # Try generous sizes first, shrink until the page fits in 1024px.
    candidates = [
        (30, 21, 27, 25),
        (29, 20, 26, 24),
        (28, 20, 25, 23),
        (27, 19, 24, 22),
    ]
    for hl_size, body_size, body_lh, lead_body_size in candidates:
        img, total = render(hl_size, body_size, body_lh, lead_body_size)
        if total <= H - 20:
            break
    img.save(out_path, "PNG", optimize=True)
    print(f"wrote {out_path} ({img.size[0]}x{img.size[1]}) "
          f"hl={hl_size} body={body_size} lead={lead_body_size} bottom={total}")


if __name__ == "__main__":
    main()
