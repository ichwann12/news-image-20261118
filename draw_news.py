#!/usr/bin/env python3
"""Draw the news-image-20261118 entry: a newspaper front page summing up
Wednesday 18 November 2026, rendered with Pillow to entry.png (1024x1024).

All facts are the verified headlines of 18 Nov 2026. No network is used.
Run:  python3 draw_news.py   (writes entry.png next to this script)
"""

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

# --- palette -------------------------------------------------------------
INK = (17, 24, 39)          # near-black text
PAPER = (255, 255, 255)
NAVY = (11, 31, 58)         # masthead bar
RED = (200, 16, 46)         # breaking / accent
RED_DARK = (160, 12, 36)
GOLD = (184, 134, 11)
RULE = (209, 213, 219)      # light grey rules
MUTED = (75, 85, 99)        # grey body text
PANEL = (248, 249, 250)     # faint panel grey

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
F_BOLD = FONT_DIR + "DejaVuSans-Bold.ttf"
F_REG = FONT_DIR + "DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_width):
    """Greedy word-wrap returning a list of lines that fit max_width px."""
    lines = []
    for para in text.split("\n"):
        words = para.split()
        if not words:
            lines.append("")
            continue
        cur = words[0]
        for word in words[1:]:
            trial = cur + " " + word
            if draw.textlength(trial, font=fnt) <= max_width:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


def draw_centered(draw, y, text, fnt, fill, width=W):
    draw.text(((width - draw.textlength(text, font=fnt)) / 2, y),
              text, font=fnt, fill=fill)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---------- masthead ----------
    d.rectangle([0, 0, W, 104], fill=NAVY)
    # thin gold rule under masthead
    d.rectangle([0, 104, W, 108], fill=GOLD)
    masthead_font = font(F_BOLD, 54)
    draw_centered(d, 22, "THE WORLD IN ONE IMAGE", masthead_font, (255, 255, 255))
    # small globe glyph: circle + meridians, left of title is crowded, so put
    # a small red square bullet flanking the date strip instead.

    # ---------- date strip ----------
    d.rectangle([0, 108, W, 150], fill=RED)
    date_font = font(F_BOLD, 27)
    draw_centered(d, 116, "WEDNESDAY  18  NOVEMBER  2026", date_font,
                  (255, 255, 255))

    y = 168

    # ---------- hero story: Iran / Gulf ----------
    tag_font = font(F_BOLD, 20)
    tag = "  BREAKING  "
    tag_w = d.textlength(tag, font=tag_font) + 8
    d.rectangle([40, y, 40 + tag_w, y + 32], fill=RED)
    d.text((44, y + 5), tag, font=tag_font, fill=(255, 255, 255))
    y += 44

    hero_font = font(F_BOLD, 47)
    hero_head = "IRAN STRIKES GULF BASES"
    d.text((40, y), hero_head, font=hero_font, fill=RED_DARK)
    y += 62

    body_font = font(F_REG, 22)
    hero_body = ("Iran launched drones and strikes at Ali Al Salem Air Base in "
                 "Kuwait and targets in Bahrain, after US aircraft hit an "
                 "Iranian missile site on Qeshm Island.")
    for line in wrap(d, hero_body, body_font, W - 80):
        d.text((40, y), line, font=body_font, fill=INK)
        y += 30
    y += 14

    # rule under hero
    d.line([(40, y), (W - 40, y)], fill=RULE, width=2)
    y += 18

    # ---------- story grid: 2 columns x 3 rows ----------
    stories = [
        ("KERCH BRIDGE HIT", (14, 116, 144),
         "Ukrainian drones and missiles partly collapse the Crimea bridge; "
         "one arch falls into the strait."),
        ("XI MEETS PUTIN", (109, 40, 217),
         "Xi and Putin meet in Shenzhen at APEC ahead of Thursday's "
         "trilateral summit with Trump."),
        ("QUAD MEETS IN MANILA", (194, 65, 12),
         "First leader-level Quad meeting in 2+ years; Trump announces a "
         "trade deal with the Philippines."),
        ("DEMOCRATS TAKE SENATE", (21, 128, 61),
         "Mary Peltola beats Dan Sullivan in Alaska; Democrats take a "
         "56\u201344 Senate majority."),
        ("GAZA CEASEFIRE STRAIN", (185, 28, 28),
         "Board of Peace faults Israel and Hamas over ceasefire "
         "commitments; 950,000 displaced Palestinians face floods (WHO)."),
        ("EBOLA IN DR CONGO", (180, 83, 9),
         "Outbreak passes 11,000 cases; three in four infected children "
         "under five die."),
    ]

    head_font = font(F_BOLD, 26)
    small_font = font(F_REG, 19)
    col_w = (W - 80 - 36) // 2          # two columns, 36px gutter
    row_h = 160
    grid_top = y
    for i, (head, color, body) in enumerate(stories):
        col = i % 2
        row = i // 2
        x0 = 40 + col * (col_w + 36)
        y0 = grid_top + row * row_h
        # coloured left bar
        d.rectangle([x0, y0 + 4, x0 + 7, y0 + 120], fill=color)
        tx = x0 + 20
        # headline (one line at this width)
        lines = wrap(d, head, head_font, col_w - 20)
        hy = y0
        for line in lines[:2]:
            d.text((tx, hy), line, font=head_font, fill=INK)
            hy += 32
        by = y0 + 42
        # body, at most 3 lines
        blines = wrap(d, body, small_font, col_w - 20)
        if len(blines) > 3:
            print("WARNING: story overflows:", head, "->", len(blines), "lines")
        for line in blines[:3]:
            d.text((tx, by), line, font=small_font, fill=MUTED)
            by += 25
        # horizontal rule under each row except the last
        if row < 2:
            d.line([(40, y0 + row_h - 12), (W - 40, y0 + row_h - 12)],
                   fill=RULE, width=1)
    y = grid_top + 3 * row_h + 4

    # ---------- ALSO TODAY strip ----------
    strip_top = y + 6
    d.rectangle([0, strip_top, W, strip_top + 118], fill=PANEL)
    d.line([(0, strip_top), (W, strip_top)], fill=RULE, width=2)
    d.line([(0, strip_top + 118), (W, strip_top + 118)], fill=RULE, width=2)
    also_font = font(F_BOLD, 21)
    d.text((40, strip_top + 10), "ALSO TODAY", font=also_font, fill=NAVY)
    also_font_body = font(F_REG, 19)
    also_text = ("Knesset elects Matan Kahana speaker  \u00b7  US loses measles-free "
                 "status after 26 years  \u00b7  NVIDIA posts record $115.84B revenue  "
                 "\u00b7  Russian military plane crashes in Siberia, 19 dead  \u00b7  "
                 "Cyber outages hit Zoom, CNN, HSBC and IKEA  \u00b7  \u201cHuman\u201d is "
                 "Cambridge Dictionary\u2019s Word of the Year")
    ay = strip_top + 40
    for line in wrap(d, also_text, also_font_body, W - 80):
        d.text((40, ay), line, font=also_font_body, fill=MUTED)
        ay += 25

    # ---------- footer ----------
    foot_font = font(F_REG, 18)
    draw_centered(d, H - 34, "Sources: Reuters  \u00b7  AP  \u00b7  AFP",
                  foot_font, MUTED)

    img.save("entry.png", format="PNG", optimize=True)
    print("wrote entry.png", img.size)


if __name__ == "__main__":
    main()
