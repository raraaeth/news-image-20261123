#!/usr/bin/env python3
"""Dense one-page newspaper renderer for the 23 November 2026 edition.

Reads stories.json (same directory) and writes a 1024x1024 PNG.
Usage: python3 render_image.py [output-path]   (default: entry.png here)
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W = H = 1024
MARGIN = 24
CW = W - 2 * MARGIN  # 976

PAPER = (247, 241, 227)
TINT = (253, 250, 242)
BAND = (238, 229, 203)
INK = (26, 23, 18)
RED = (176, 42, 30)
BLUE = (31, 58, 95)
FAINT = (112, 102, 86)
MAPDOT = (94, 100, 110)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF_B = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")
SANS_B = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")


def F(path, size):
    return ImageFont.truetype(path, size)


def tw(draw, s, font):
    return draw.textlength(s, font=font)


def wrap(draw, text, font, maxw):
    """Greedy word wrap; returns list of lines that each fit maxw."""
    lines = []
    for para in text.split("\n"):
        cur = ""
        for word in para.split(" "):
            trial = word if not cur else cur + " " + word
            if tw(draw, trial, font) <= maxw or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


def fit_font(draw, text, path, maxw, max_lines, start, minimum):
    """Largest font size (<= start, >= minimum) whose wrap fits max_lines."""
    size = start
    while size > minimum:
        font = F(path, size)
        if len(wrap(draw, text, font, maxw)) <= max_lines:
            return font
        size -= 1
    return F(path, minimum)


def draw_lines(draw, x, y, lines, font, lh, fill=INK):
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += lh
    return y


def section_header(draw, x, y, title, width=CW):
    """Small red square + bold caps title + hair rule to the right."""
    font = F(SANS_B, 12)
    draw.rectangle([x, y + 2, x + 8, y + 10], fill=RED)
    draw.text((x + 14, y), title, font=font, fill=INK)
    tx = x + 14 + tw(draw, title, font)
    draw.line([tx + 10, y + 7, x + width, y + 7], fill=FAINT, width=1)
    return y + 16


def badge(draw, x, y, n):
    """Red number badge; returns width used."""
    label = str(n)
    font = F(SANS_B, 10)
    wdt = int(tw(draw, label, font)) + 8
    draw.rectangle([x, y, x + wdt, y + 14], fill=RED)
    draw.text((x + 4, y + 2), label, font=font, fill=(255, 255, 255))
    return wdt


# ---------------------------------------------------------------- map data
# Coarse world landmass, 96 cols x 40 rows, as (first, last) land runs.
LAND_RUNS = {
    0: [(20, 30), (56, 58), (60, 66), (71, 76), (82, 86)],
    1: [(2, 10), (14, 28), (30, 38), (54, 56), (58, 66), (70, 78), (82, 90)],
    2: [(1, 12), (14, 34), (36, 40), (44, 46), (53, 58), (59, 92)],
    3: [(2, 13), (15, 36), (38, 39), (44, 45), (53, 57), (58, 93)],
    4: [(3, 10), (16, 38), (47, 48), (53, 58), (59, 92)],
    5: [(17, 39), (46, 48), (52, 90)],
    6: [(18, 40), (42, 43), (45, 48), (50, 91)],
    7: [(17, 41), (48, 90)],
    8: [(16, 41), (47, 89)],
    9: [(15, 41), (46, 60), (62, 88), (89, 90)],
    10: [(14, 41), (46, 48), (51, 58), (60, 72), (74, 87), (88, 90)],
    11: [(14, 40), (46, 47), (55, 59), (61, 71), (74, 86), (88, 89)],
    12: [(13, 40), (45, 58), (59, 64), (65, 70), (74, 85), (88, 89)],
    13: [(13, 30), (33, 35), (44, 60), (61, 65), (66, 73), (75, 84)],
    14: [(14, 27), (43, 59), (60, 64), (67, 73), (76, 82)],
    15: [(42, 58), (59, 64), (67, 72), (76, 80)],
    16: [(15, 20), (41, 57), (68, 71), (76, 79), (83, 84)],
    17: [(40, 55), (68, 70), (75, 78), (83, 84)],
    18: [(24, 32), (39, 52), (60, 62), (75, 78), (85, 90)],
    19: [(25, 34), (38, 50), (80, 92)],
    20: [(25, 35), (39, 49), (79, 93)],
    21: [(26, 36), (40, 48), (78, 92)],
    22: [(26, 36), (41, 47), (79, 90)],
    23: [(27, 36), (41, 47), (80, 91)],
    24: [(27, 35), (42, 46), (75, 79), (81, 88)],
    25: [(27, 34), (42, 46), (74, 79), (83, 90)],
    26: [(28, 34), (42, 46), (82, 90)],
    27: [(28, 33), (43, 46), (81, 91)],
    28: [(28, 33), (43, 45), (47, 48), (81, 91)],
    29: [(28, 32), (43, 45), (82, 90)],
    30: [(28, 32), (43, 45), (82, 90)],
    31: [(29, 32), (43, 44), (83, 89)],
    32: [(29, 31), (43, 44), (84, 89), (94, 95)],
    33: [(29, 31), (85, 88), (93, 95)],
    34: [(29, 30), (92, 94)],
    35: [(29, 30), (91, 93)],
    36: [(29, 30)],
}
# (column, row) of story locations on the grid above.
LOCATIONS = [
    (56, 5),    # St Petersburg
    (56, 8),    # Kyiv / Dymer
    (47, 11),   # Madrid
    (56, 12),   # Antalya
    (16, 12),   # California
    (82, 12),   # Seoul
    (53, 13),   # Benghazi
    (69, 14),   # Delhi
    (63, 15),   # Hormuz
    (76, 25),   # Cikande
]


def draw_map(draw, x, y, width, height):
    cols, rows = 96, 40
    cw = width / cols
    ch = height / rows
    r = max(1.1, min(cw, ch) * 0.34)
    for row, runs in LAND_RUNS.items():
        cy = y + (row + 0.5) * ch
        for a, b in runs:
            for col in range(a, b + 1):
                cx = x + (col + 0.5) * cw
                draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=MAPDOT)
    for col, row in LOCATIONS:
        cx = x + (col + 0.5) * cw
        cy = y + (row + 0.5) * ch
        draw.ellipse([cx - 4.4, cy - 4.4, cx + 4.4, cy + 4.4], fill=RED)
        draw.ellipse([cx - 4.4, cy - 4.4, cx + 4.4, cy + 4.4],
                     outline=(255, 255, 255), width=1)


# ------------------------------------------------------------- motifs
def motif_globe(draw, cx, cy):
    r = 19
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=INK, width=2)
    draw.ellipse([cx - 8, cy - r, cx + 8, cy + r], outline=INK, width=1)
    draw.ellipse([cx - 15, cy - r, cx + 15, cy + r], outline=INK, width=1)
    draw.line([cx - r, cy, cx + r, cy], fill=INK, width=1)
    draw.line([cx - 16, cy - 10, cx + 16, cy - 10], fill=INK, width=1)
    draw.line([cx - 16, cy + 10, cx + 16, cy + 10], fill=INK, width=1)
    crack = [(cx - 6, cy - 18), (cx, cy - 8), (cx - 7, cy + 1),
             (cx + 1, cy + 9), (cx - 4, cy + 18)]
    draw.line(crack, fill=RED, width=3, joint="curve")


def motif_chip(draw, cx, cy):
    draw.rounded_rectangle([cx - 17, cy - 15, cx + 17, cy + 15],
                           radius=3, outline=INK, width=2)
    draw.rectangle([cx - 8, cy - 7, cx + 8, cy + 7], fill=BLUE)
    for dx in (-10, 0, 10):
        draw.line([cx + dx, cy - 21, cx + dx, cy - 15], fill=INK, width=2)
        draw.line([cx + dx, cy + 15, cx + dx, cy + 21], fill=INK, width=2)
    for dy in (-7, 0, 7):
        draw.line([cx - 23, cy + dy, cx - 17, cy + dy], fill=INK, width=2)
        draw.line([cx + 17, cy + dy, cx + 23, cy + dy], fill=INK, width=2)
    draw.line([cx - 8, cy + 18, cx + 8, cy + 18], fill=RED, width=2)


def motif_factory(draw, cx, cy):
    base = cy + 19
    draw.rectangle([cx - 30, cy + 2, cx - 8, base], outline=INK, width=2)
    draw.rectangle([cx - 6, cy - 4, cx + 16, base], outline=INK, width=2)
    draw.rectangle([cx + 20, cy - 12, cx + 26, base], fill=INK)
    for wx in (-25, -17):
        draw.rectangle([wx + cx, cy + 7, wx + cx + 4, cy + 11], fill=BLUE)
    for wx in (0, 7):
        draw.rectangle([wx + cx, cy + 2, wx + cx + 4, cy + 6], fill=BLUE)
    flame = [(cx + 23, cy - 30), (cx + 29, cy - 16), (cx + 26, cy - 11),
             (cx + 20, cy - 11), (cx + 17, cy - 16)]
    draw.polygon(flame, fill=RED)
    inner = [(cx + 23, cy - 22), (cx + 26, cy - 15), (cx + 23, cy - 12),
             (cx + 20, cy - 15)]
    draw.polygon(inner, fill=(232, 126, 32))
    draw.line([cx - 34, base, cx + 34, base], fill=INK, width=2)


MOTIFS = {"globe": motif_globe, "chip": motif_chip, "factory": motif_factory}


# ------------------------------------------------------------- panels
def panel_large(draw, x, y, w, h, p):
    """Illustration band, badge+kicker, serif headline, body."""
    draw.rectangle([x, y, x + w, y + 44], fill=BAND)
    MOTIFS[p["motif"]](draw, x + w // 2, y + 22)
    cy = y + 50
    bw = badge(draw, x + 2, cy, p["n"])
    draw.text((x + 2 + bw + 7, cy + 1), p["kicker"], font=F(SANS_B, 11),
              fill=BLUE)
    cy += 17
    hfont = fit_font(draw, p["headline"], SERIF_B, w - 4, 2, 20, 15)
    lines = wrap(draw, p["headline"], hfont, w - 4)
    cy = draw_lines(draw, x + 2, cy, lines, hfont, 23)
    cy += 2
    bfont = fit_font(draw, p["body"], SANS, w - 6, 6, 12, 9)
    lines = wrap(draw, p["body"], bfont, w - 6)
    draw_lines(draw, x + 2, cy, lines, bfont, 13)


def panel_small(draw, x, y, w, h, p):
    bw = badge(draw, x + 1, y, p["n"])
    draw.text((x + 1 + bw + 6, y + 1), p["kicker"], font=F(SANS_B, 9),
              fill=BLUE)
    cy = y + 16
    hfont = fit_font(draw, p["headline"], SERIF_B, w - 2, 3, 13, 10)
    lines = wrap(draw, p["headline"], hfont, w - 2)
    cy = draw_lines(draw, x + 1, cy, lines, hfont, 14)
    cy += 1
    bfont = fit_font(draw, p["body"], SANS, w - 3, 5, 10, 8)
    lines = wrap(draw, p["body"], bfont, w - 3)
    draw_lines(draw, x + 1, cy, lines, bfont, 11)


# ------------------------------------------------------------- main
def render(data, out_path):
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    x0 = MARGIN
    xr = MARGIN + CW

    # --- masthead line
    mf = F(SANS_B, 14)
    draw.text((x0, 13), data["masthead_left"], font=mf, fill=INK)
    rtxt = data["masthead_right"]
    draw.text((xr - tw(draw, rtxt, mf), 13), rtxt, font=mf, fill=RED)
    draw.line([x0, 33, xr, 33], fill=INK, width=2)

    # --- giant date
    dfont = fit_font(draw, data["date"], SERIF_B, 940, 1, 110, 40)
    dwidth = tw(draw, data["date"], dfont)
    draw.text(((W - dwidth) / 2, 40), data["date"], font=dfont, fill=INK)

    # --- weekday with side rules
    wf = F(SANS_B, 21)
    word = data["weekday"]
    spacing = 14
    total = sum(tw(draw, c, wf) for c in word) + spacing * (len(word) - 1)
    sx = (W - total) / 2
    wy = 128
    draw.line([x0, wy + 11, sx - 18, wy + 11], fill=INK, width=1)
    draw.line([sx + total + 18, wy + 11, xr, wy + 11], fill=INK, width=1)
    cx = sx
    for c in word:
        draw.text((cx, wy), c, font=wf, fill=RED)
        cx += tw(draw, c, wf) + spacing
    draw.rectangle([x0, 158, xr, 160], fill=INK)
    draw.line([x0, 164, xr, 164], fill=INK, width=1)

    # --- THE DAY IN BRIEF
    y = section_header(draw, x0, 172, data["brief"]["title"])
    colw = CW / 6
    # Shrink the strip font until every item wraps to at most 3 lines,
    # so no item's text can spill past the strip's bottom rule.
    bsize = 11
    while bsize > 8 and any(
            len(wrap(draw, it["text"], F(SANS, bsize), colw - 12)) > 3
            for it in data["brief"]["items"]):
        bsize -= 1
    bfont = F(SANS, bsize)
    for i, item in enumerate(data["brief"]["items"]):
        cx = x0 + i * colw
        if i:
            draw.line([cx - 6, y + 2, cx - 6, y + 52], fill=FAINT, width=1)
        draw.text((cx, y), item["part"], font=F(SANS_B, 10), fill=RED)
        lines = wrap(draw, item["text"], bfont, colw - 12)
        draw_lines(draw, cx, y + 14, lines, bfont, 12)
    draw.line([x0, 248, xr, 248], fill=INK, width=1)

    # --- THE DAY IN NUMBERS
    y = section_header(draw, x0, 256, data["numbers"]["title"])
    vfont = F(SERIF_B, 23)
    cfont = F(SANS, 10)
    for i, item in enumerate(data["numbers"]["items"]):
        cx = x0 + i * colw
        if i:
            draw.line([cx - 6, y + 2, cx - 6, y + 54], fill=FAINT, width=1)
        vw = tw(draw, item["value"], vfont)
        draw.text((cx + (colw - 12 - vw) / 2, y), item["value"], font=vfont,
                  fill=RED)
        lines = wrap(draw, item["caption"], cfont, colw - 14)
        ly = y + 27
        for line in lines:
            lw = tw(draw, line, cfont)
            draw.text((cx + (colw - 12 - lw) / 2, ly), line, font=cfont,
                      fill=INK)
            ly += 11
    draw.line([x0, 334, xr, 334], fill=INK, width=1)

    # --- large panels 1-3
    ly = 342
    lw3 = (CW - 24) / 3
    for i, p in enumerate(data["panels_large"]):
        px = x0 + i * (lw3 + 12)
        if i:
            draw.line([px - 6, ly, px - 6, ly + 192], fill=FAINT, width=1)
        panel_large(draw, px, ly, lw3, 196, p)
    draw.line([x0, 542, xr, 542], fill=INK, width=1)

    # --- small panels 4-13, two rows of five
    sw = (CW - 40) / 5
    for r in range(2):
        ry = 550 + r * 120
        if r:
            draw.line([x0, ry - 6, xr, ry - 6], fill=FAINT, width=1)
        for c in range(5):
            p = data["panels_small"][r * 5 + c]
            px = x0 + c * (sw + 10)
            if c:
                draw.line([px - 5, ry, px - 5, ry + 106], fill=FAINT, width=1)
            panel_small(draw, px, ry, sw, 112, p)
    draw.line([x0, 784, xr, 784], fill=INK, width=1)

    # --- bottom band: map (left) + also on (right)
    by = 792
    section_header(draw, x0, by, data["map_title"], width=452)
    draw_map(draw, x0, by + 20, 452, 140)
    ax = x0 + 476
    aw = xr - ax
    section_header(draw, ax, by, data["also_on"]["title"], width=aw)
    draw.line([ax - 12, by + 2, ax - 12, by + 158], fill=FAINT, width=1)
    nfont = F(SANS_B, 10)
    tfont = F(SANS, 10)
    acolw = (aw - 14) / 2
    col_y = [by + 19, by + 19]
    for j, item in enumerate(data["also_on"]["items"]):
        col = 0 if j < 5 else 1
        ix = ax + col * (acolw + 14)
        iy = col_y[col]
        num = str(14 + j)
        draw.text((ix, iy), num, font=nfont, fill=RED)
        lines = wrap(draw, item, tfont, acolw - 20)
        draw_lines(draw, ix + 20, iy, lines, tfont, 11.5)
        col_y[col] = iy + len(lines) * 11.5 + 3

    # --- date check box
    ky = 962
    draw.rectangle([x0, ky, xr, ky + 32], outline=INK, width=1)
    kfont = F(SANS, 10)
    legend = data["legend"]
    lfont = F(SANS_B, 10)
    lw_legend = tw(draw, legend, lfont)
    lines = wrap(draw, data["date_check"], kfont, CW - lw_legend - 34)
    draw_lines(draw, x0 + 9, ky + 5, lines, kfont, 12)
    draw.text((xr - lw_legend - 9, ky + 11), legend, font=lfont, fill=BLUE)

    # --- footer
    ffont = F(SANS, 10)
    ftxt = data["footer"]
    draw.text(((W - tw(draw, ftxt, ffont)) / 2, 1002), ftxt, font=ffont,
              fill=FAINT)

    img.save(out_path, "PNG", optimize=True)
    return out_path


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "entry.png")
    with open(os.path.join(HERE, "stories.json"), encoding="utf-8") as fh:
        data = json.load(fh)
    render(data, out)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
