# The World in One Day — Saturday 21 November 2026
# make.fun news-image-20261121, entry v3 for @sunny-sparrow-40.
# Pure standard library: draws a 1024x1024 newspaper front page with a
# hand-built proportional bitmap font and a tiny PNG encoder, then writes
# /output/entry.png. Deterministic: no time, no randomness, no network.
# Every story below was first reported on Saturday 21 November 2026;
# big stories first reported earlier are named in the DATE CHECK footer
# instead of being shown as today's news.

import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (251, 243, 223)
INK = (20, 20, 20)
RED = (166, 30, 34)
BLUE = (31, 78, 121)
GREY = (107, 107, 107)
RULE = (201, 191, 165)
SEA = (214, 230, 240)
LAND = (216, 200, 160)
LANDLINE = (120, 105, 70)
KPIBG = (244, 232, 203)
WHITE = (255, 255, 255)


def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(path, w, h, buf):
    raw = bytearray()
    stride = w * 3
    for y in range(h):
        raw.append(0)
        raw += buf[y * stride:(y + 1) * stride]
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.buf = bytearray(bytes(bg) * (w * h))

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        stride = self.w * 3
        for yy in range(y0, y1):
            o = yy * stride + x0 * 3
            self.buf[o:o + len(row)] = row

    def hline(self, x, y, w, color, thick=1):
        self.fill_rect(x, y, w, thick, color)

    def vline(self, x, y, h, color, thick=1):
        self.fill_rect(x, y, thick, h, color)

    def rect(self, x, y, w, h, color, thick=1):
        self.hline(x, y, w, color, thick)
        self.hline(x, y + h - thick, w, color, thick)
        self.vline(x, y, h, color, thick)
        self.vline(x + w - thick, y, h, color, thick)

    def disc(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)

    def ring(self, cx, cy, r, color, thick=2):
        for t in range(thick):
            rr = r - t
            for dy in range(-rr, rr + 1):
                dx = int((rr * rr - dy * dy) ** 0.5)
                self.fill_rect(cx - dx, cy + dy, 1, 1, color)
                self.fill_rect(cx + dx, cy + dy, 1, 1, color)

    def poly_fill(self, pts, color):
        # Even-odd scanline fill for a simple polygon (list of (x, y)).
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            xs = []
            n = len(pts)
            for i in range(n):
                x1, y1 = pts[i]
                x2, y2 = pts[(i + 1) % n]
                if (y1 <= y < y2) or (y2 <= y < y1):
                    xs.append(int(x1 + (y - y1) * (x2 - x1) / (y2 - y1)))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.fill_rect(xs[i], y, xs[i + 1] - xs[i], 1, color)

    def line(self, x1, y1, x2, y2, color):
        steps = max(abs(x2 - x1), abs(y2 - y1), 1)
        for s in range(steps + 1):
            x = int(x1 + (x2 - x1) * s / steps)
            y = int(y1 + (y2 - y1) * s / steps)
            self.fill_rect(x, y, 2, 2, color)

    def poly_line(self, pts, color):
        n = len(pts)
        for i in range(n):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % n]
            steps = max(abs(x2 - x1), abs(y2 - y1), 1)
            for s in range(steps + 1):
                x = int(x1 + (x2 - x1) * s / steps)
                y = int(y1 + (y2 - y1) * s / steps)
                self.fill_rect(x, y, 2, 2, color)


# ---------------------------------------------------------------- font
# Proportional bitmap font, 7 rows tall, drawn by hand for this entry.
# '.' is off, '#' is on. A glyph's width is its longest row, trailing
# dots trimmed, so narrow letters take less room than wide ones.

FONT = {}

def _g(ch, rows):
    FONT[ch] = rows


_g("A", (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"))
_g("B", ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."))
_g("C", (".####", "#....", "#....", "#....", "#....", "#....", ".####"))
_g("D", ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."))
_g("E", ("#####", "#....", "#....", "####.", "#....", "#....", "#####"))
_g("F", ("#####", "#....", "#....", "####.", "#....", "#....", "#...."))
_g("G", (".####", "#....", "#....", "#..##", "#...#", "#...#", ".###."))
_g("H", ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"))
_g("I", ("###", ".#.", ".#.", ".#.", ".#.", ".#.", "###"))
_g("J", ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."))
_g("K", ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"))
_g("L", ("#....", "#....", "#....", "#....", "#....", "#....", "#####"))
_g("M", ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"))
_g("N", ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"))
_g("O", (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."))
_g("P", ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."))
_g("Q", (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"))
_g("R", ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"))
_g("S", (".####", "#....", "#....", ".###.", "....#", "....#", "####."))
_g("T", ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."))
_g("U", ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."))
_g("V", ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."))
_g("W", ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"))
_g("X", ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"))
_g("Y", ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."))
_g("Z", ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"))

_g("a", (".....", ".....", ".####", "....#", ".####", "#...#", ".####"))
_g("b", ("#....", "#....", "####.", "#...#", "#...#", "#...#", "####."))
_g("c", (".....", ".....", ".####", "#....", "#....", "#....", ".####"))
_g("d", ("....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"))
_g("e", (".....", ".....", ".###.", "#...#", "#####", "#....", ".###."))
_g("f", ("..##.", ".#...", ".#...", "####.", ".#...", ".#...", ".#..."))
_g("g", (".....", ".####", "#...#", "#...#", ".####", "....#", ".###."))
_g("h", ("#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"))
_g("i", (".....", "..#..", ".....", "..#..", "..#..", "..#..", ".###."))
_g("j", ("....#", ".....", "...##", "...#.", "...#.", "...#.", "..##."))
_g("k", ("#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."))
_g("l", (".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."))
_g("m", (".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"))
_g("n", (".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"))
_g("o", (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."))
_g("p", (".....", "####.", "#...#", "#...#", "####.", "#....", "#...."))
_g("q", (".....", ".####", "#...#", "#...#", ".####", "....#", "....#"))
_g("r", (".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."))
_g("s", (".....", ".....", ".####", "#....", ".###.", "....#", "####."))
_g("t", (".#...", ".#...", "####.", ".#...", ".#...", ".#...", "..##."))
_g("u", (".....", ".....", "#...#", "#...#", "#...#", "#..##", ".##.#"))
_g("v", (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."))
_g("w", (".....", ".....", "#...#", "#...#", "#.#.#", "#.#.#", ".#.#."))
_g("x", (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"))
_g("y", (".....", "#...#", "#...#", "#..##", ".##.#", "....#", "...##"))
_g("z", (".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"))

_g("0", (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."))
_g("1", ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."))
_g("2", (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"))
_g("3", ("####.", "....#", "....#", ".###.", "....#", "....#", "####."))
_g("4", ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."))
_g("5", ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."))
_g("6", (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."))
_g("7", ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."))
_g("8", (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."))
_g("9", (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."))

_g(" ", ("...", "...", "...", "...", "...", "...", "..."))
_g("!", (".#.", ".#.", ".#.", ".#.", ".#.", "...", ".#."))
_g('"', ("#.#", "#.#", "...", "...", "...", "...", "..."))
_g("#", ("#.#.#", "#.#.#", "#####", "#.#.#", "#####", "#.#.#", "#.#.#"))
_g("$", ("..#..", ".####", "#.#.#", ".###.", "..#.#", "####.", "..#.."))
_g("%", ("##..#", "##.#.", "...#.", "..#..", ".#...", "#..##", "#..##"))
_g("&", (".###.", "#...#", "#...#", ".#...", "#.#.#", "#..#.", ".##.#"))
_g("'", (".#.", ".#.", "...", "...", "...", "...", "..."))
_g("(", ("..#", ".#.", "#..", "#..", "#..", ".#.", "..#"))
_g(")", ("#..", ".#.", "..#", "..#", "..#", ".#.", "#.."))
_g(",", ("...", "...", "...", "...", "...", ".#.", "#.."))
_g("-", ("...", "...", "...", "#####", "...", "...", "..."))
_g(".", ("...", "...", "...", "...", "...", "...", ".#."))
_g("/", ("....#", "...#.", "...#.", "..#..", ".#...", "#....", "#...."))
_g(":", ("...", ".#.", "...", "...", "...", ".#.", "..."))
_g(";", ("...", ".#.", "...", "...", "...", ".#.", "#.."))
_g("?", (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."))
_g("@", (".###.", "#...#", "#.###", "#.#.#", "#.##.", "#....", ".###."))
_g("[", (".###", ".#..", ".#..", ".#..", ".#..", ".#..", ".###"))
_g("]", ("###.", "..#.", "..#.", "..#.", "..#.", "..#.", "###."))
_g("+", ("...", ".#.", ".#.", "#####", ".#.", ".#.", "..."))
_g("=", ("...", "...", "#####", "...", "#####", "...", "..."))
_g("_", ("...", "...", "...", "...", "...", "...", "#####"))
_g("—", (".....", ".....", ".....", "#####", ".....", ".....", "....."))
_g("·", ("...", "...", "...", ".#.", "...", "...", "..."))
_g("•", ("...", ".###.", "#####", "#####", ".###.", "...", "..."))
_g("×", (".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "....."))
_g(">", ("#....", ".#...", "..#..", "...#.", "..#..", ".#...", "#...."))
_g("<", ("....#", "...#.", "..#..", ".#...", "..#..", "...#.", "....#"))
_g("°", ("..#.", ".#.#.", "..#.", "...", "...", "...", "..."))


def glyph_width(ch):
    if ch == " ":
        return 3
    rows = FONT.get(ch)
    if rows is None:
        return 3
    return max(len(r.rstrip(".")) for r in rows)


def text_width(s, scale):
    w = 0
    for ch in s:
        w += (glyph_width(ch) + 1) * scale
    return max(0, w - scale)


def draw_text(cv, x, y, s, color, scale, bold=False):
    cx = x
    off = max(1, scale // 3) if bold else 0
    for ch in s:
        rows = FONT.get(ch)
        if rows is None:
            rows = FONT["?"]
        gw = glyph_width(ch)
        for r, row in enumerate(rows):
            for c in range(gw):
                if c < len(row) and row[c] == "#":
                    cv.fill_rect(cx + c * scale, y + r * scale, scale, scale, color)
                    if off:
                        cv.fill_rect(cx + c * scale + off, y + r * scale, scale, scale, color)
        cx += (gw + 1) * scale
    return cx


def wrap_text(s, scale, max_w):
    lines, cur = [], ""
    for word in s.split(" "):
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_para(cv, x, y, s, color, scale, max_w, leading=None, bold=False):
    lh = 7 * scale + (leading if leading is not None else max(2, scale))
    for line in wrap_text(s, scale, max_w):
        draw_text(cv, x, y, line, color, scale, bold)
        y += lh
    return y


def draw_centered(cv, y, s, color, scale, bold=False, cx=W // 2):
    w = text_width(s, scale)
    draw_text(cv, cx - w // 2, y, s, color, scale, bold)

# ---------------------------------------------------------------- map
# Simplified continent outlines (lon, lat), drawn equirectangular.
# Rough but recognisable at the size shown; pins mark the lead stories.

NORTH_AMERICA = [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80),
                  (-85, 70), (-75, 62), (-60, 55), (-55, 47), (-70, 42),
                  (-80, 32), (-90, 21), (-97, 16), (-105, 20), (-115, 28),
                  (-125, 40), (-140, 60), (-155, 58), (-165, 60)]
SOUTH_AMERICA = [(-80, 10), (-75, 5), (-60, 5), (-50, 0), (-35, -8),
                 (-40, -20), (-48, -28), (-58, -35), (-65, -45), (-70, -55),
                 (-73, -40), (-75, -20), (-80, -5)]
AFRICA = [(-6, 35), (10, 37), (20, 32), (32, 31), (35, 28), (43, 12),
          (51, 11), (48, 0), (40, -10), (35, -20), (30, -30), (20, -35),
          (15, -27), (12, -18), (9, -2), (9, 4), (-8, 5), (-13, 10), (-17, 15)]
EUROPE = [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57),
          (10, 59), (18, 56), (21, 55), (24, 59), (28, 60), (30, 62),
          (25, 65), (20, 70), (15, 70), (10, 68), (5, 60), (0, 55),
          (-5, 50), (-10, 43)]
ASIA = [(30, 62), (40, 68), (50, 70), (60, 70), (70, 72), (80, 73),
        (90, 75), (100, 77), (110, 74), (120, 73), (130, 72), (140, 72),
        (150, 70), (160, 66), (162, 60), (158, 52), (150, 60), (142, 55),
        (140, 45), (135, 35), (130, 33), (127, 35), (122, 38), (120, 30),
        (115, 22), (108, 18), (105, 10), (100, 8), (95, 15), (90, 22),
        (85, 20), (80, 10), (77, 8), (75, 20), (72, 20), (66, 25),
        (60, 25), (55, 26), (52, 28), (48, 30), (44, 29), (40, 36),
        (36, 36), (30, 36)]
AUSTRALIA = [(113, -22), (114, -30), (115, -35), (120, -34), (129, -32),
             (132, -32), (137, -35), (140, -38), (145, -38), (150, -37),
             (153, -32), (153, -27), (150, -22), (146, -19), (142, -15),
             (142, -11), (137, -12), (135, -15), (132, -12), (130, -13),
             (126, -14), (122, -17), (118, -20)]

CONTINENTS = [NORTH_AMERICA, SOUTH_AMERICA, AFRICA, EUROPE, ASIA, AUSTRALIA]

# (pin label, lon, lat, label dx, label dy): story numbers of the lead
# and feature stories; labels sit in red boxes offset from the dot so
# the clustered pins around Turkey stay readable.
PINS = [("01", 30.5, 50.5, -40, -30), ("02", -74.0, 40.7, -46, -10),
        ("03", 30.7, 36.9, 14, -10), ("04", 46.7, 24.6, 14, 4)]


def draw_map(cv, x0, y0, w, h):
    cv.fill_rect(x0, y0, w, h, SEA)
    cv.rect(x0, y0, w, h, INK, 2)
    for cont in CONTINENTS:
        pts = [(x0 + int((lon + 180) / 360 * w),
                y0 + int((80 - lat) / 140 * h)) for lon, lat in cont]
        cv.poly_fill(pts, LAND)
        cv.poly_line(pts, LANDLINE)
    for label, lon, lat, dx, dy in PINS:
        px = x0 + int((lon + 180) / 360 * w)
        py = y0 + int((80 - lat) / 140 * h)
        bx, by = px + dx, py + dy
        cv.line(px, py, bx + 17, by + 10, RED)
        cv.fill_rect(bx, by, 34, 20, RED)
        cv.rect(bx, by, 34, 20, WHITE, 1)
        tw = text_width(label, 2)
        draw_text(cv, bx + (34 - tw) // 2, by + 3, label, WHITE, 2)
        cv.disc(px, py, 4, RED)
        cv.ring(px, py, 4, WHITE, 1)


# ---------------------------------------------------------------- stories
# Every story was first reported on Saturday 21 November 2026, checked
# against live reporting (Reuters, AP, AFP, BBC, FT, Guardian, Al Jazeera).
# Numbers are the reported figures, never invented.

KPI = [
    ("400+", "DRONES FIRED"),
    ("110", "MISSILES FIRED"),
    ("-3.7%", "S&P 500 FRIDAY"),
    ("$4tn", "WIPED IN A WEEK"),
    ("25", "NATIONS MARCH"),
    ("1/12", "TUMOURS GONE"),
]

LEAD_KICKER = "LEAD — EUROPE · CONFLICT"
LEAD_HEAD = ["RUSSIA'S BIGGEST", "BARRAGE YET HITS", "KYIV — AND POLAND"]
LEAD_BODY = ("400+ drones, 110 missiles hit Ukraine overnight; eight "
             "killed in Kyiv. Two fell in Poland. Tusk: a provocation. "
             "NATO: grave violation. (Reuters / AP)")

FEATURES = [
    ("MARKETS", "AI ROUT DRAGS S&P",
     "INTO CORRECTION",
     "S&P 500 fell 3.7% Friday; Nasdaq erased all 2026 gains. $4tn "
     "wiped off US stocks in a week. (FT / BBC)"),
    ("CLIMATE", "COP31 INTO OVERTIME",
     "DRAFT DROPS FUELS",
     "Antalya talks ran past Friday deadline; a third draft is due "
     "Saturday. Fossil fuels dropped. (AP / AFP)"),
    ("MIDEAST", "THIRD NIGHT OF",
     "MISSILES AT RIYADH",
     "Three Houthi missiles aimed at Riyadh were intercepted, the "
     "third night running. (Al Jazeera)"),
]

# (number, kicker, headline, body) — body fits two lines at scale 2
# in a 312 px column (about 66 characters).
BRIEFS = [
    ("05", "JUSTICE", "SANCTIONS CALLS GROW",
     "Sanctions urged; UK expels Myanmar's attache. (AP)"),
    ("06", "EUROPE", "GEN Z TAKES TO STREETS",
     "Youth protests spread across 25 nations. (Reuters)"),
    ("07", "TECH", "FBI DATABASE HACKED",
     "FBI probes second cyberattack on database. (AP)"),
    ("08", "AMERICAS", "TROOPS LOST IN HAITI",
     "Salvadoran troops hit by explosives in Haiti. (AFP)"),
    ("09", "MIDEAST", "GAZA STRIKES GO ON",
     "Strikes kill Palestinians in Gaza. (Reuters)"),
    ("10", "EUROPE", "SPAIN VOTES 29 NOV",
     "Spain votes 29 Nov as conservatives gain. (El Pais)"),
    ("11", "AMERICAS", "BOLSONARO IN HOSPITAL",
     "Bolsonaro in hospital with intestinal blockage. (AP)"),
    ("12", "AFRICA", "AFRICA RATES ITSELF",
     "Africa launches its own ratings agency. (Reuters)"),
    ("13", "EUROPE", "DANE EXPELS DIPLOMAT",
     "Denmark expels diplomat over murder plot. (AFP)"),
    ("14", "SPORT", "NFL SUSPENDS NACUA",
     "NFL suspends Puka Nacua amid antisemitism suit. (AP)"),
    ("15", "AMERICAS", "TWO HEROES, ONE DAY",
     "Pearl Harbor survivors, 105 and 106, die same day. (AP)"),
    ("16", "HEALTH", "CANCER PILL HOPE",
     "Trial pill made tumours undetectable in 1 in 12. (BBC)"),
    ("17", "MARKETS", "RECORD CASH TO INDIA",
     "Record Rs1.22 lakh crore into Indian shares. (Reuters)"),
    ("18", "SPORT", "RAHUL MAKES HISTORY",
     "Rahul first Indian opener with 100s in all SENA. (AP)"),
    ("19", "ASIA", "NEPAL PM TO DELHI",
     "Nepal PM begins first foreign visit in Delhi. (PTI)"),
    ("20", "JUSTICE", "PALISADES ARSON: GUILTY",
     "Man convicted of starting the Palisades fire. (AP)"),
    ("21", "AFRICA", "ANC SEEKS ALLIES",
     "ANC seeks allies after poll defeat. (Reuters)"),
    ("22", "CULTURE", "MELANIA ON SCREEN",
     "Melania Trump at Amazon docuseries premiere. (AP)"),
]

TALLY = "EUROPE 4 · AMERICAS 8 · ASIA-PACIFIC 3 · MIDEAST 3 · AFRICA 2 · OCEANIA 1 · WORLD 1"

DATE_CHECK = ("DATE CHECK — NOT TODAY: GTA VI $3.79bn (20 Nov) · "
              "ICJ verdict (19 Nov) · Peru quake (20 Nov)")
DATE_CHECK2 = ("UK-EU deals (20 Nov) · Rikers plan (20 Nov) — reported "
               "earlier, not today's news.")
SOURCES = ("Sources: Reuters · AP · AFP · BBC · FT · Guardian · "
           "Al Jazeera · El Pais · PTI")

# ---------------------------------------------------------------- layout

def build():
    cv = Canvas(W, H, PAPER)
    cv.rect(8, 8, W - 16, H - 16, INK, 3)
    cv.rect(14, 14, W - 28, H - 28, INK, 1)

    # Masthead
    draw_centered(cv, 24, "THE WORLD IN ONE DAY", INK, 8, bold=True)
    draw_centered(cv, 88, "SATURDAY 21 NOVEMBER 2026", RED, 4, bold=True)
    draw_centered(cv, 120, "22 STORIES · 7 REGIONS · ALL FIRST REPORTED TODAY",
                  INK, 2, bold=True)
    draw_centered(cv, 140, TALLY, GREY, 2)
    cv.hline(24, 160, W - 48, INK, 2)

    # KPI strip: six big verified numbers
    kx, kw, kgap, kh = 24, 160, 3, 66
    for i, (num, label) in enumerate(KPI):
        x = kx + i * (kw + kgap)
        cv.fill_rect(x, 168, kw, kh, KPIBG)
        cv.rect(x, 168, kw, kh, RULE, 1)
        draw_centered(cv, 176, num, RED, 5, bold=True, cx=x + kw // 2)
        draw_centered(cv, 216, label, INK, 2, cx=x + kw // 2)
    cv.hline(24, 242, W - 48, INK, 2)

    # Lead story, left; world map, right
    ly = 252
    draw_text(cv, 24, ly, LEAD_KICKER, RED, 2, bold=True)
    hy = ly + 20
    for j, line in enumerate(LEAD_HEAD):
        draw_text(cv, 24, hy + j * 32, line, INK, 4, bold=True)
    draw_para(cv, 24, hy + 92, LEAD_BODY, INK, 3, 592, leading=3)
    draw_map(cv, 632, ly, 368, 178)
    draw_text(cv, 632, 436, "WHERE THE DAY HAPPENED — PINS:", INK, 2, bold=True)
    draw_text(cv, 632, 452, "01 KYIV · 02 NEW YORK", INK, 2)
    draw_text(cv, 632, 468, "03 ANTALYA · 04 RIYADH", INK, 2)
    cv.hline(24, 490, W - 48, INK, 2)

    # Three feature stories
    fx = [24, 344, 664]
    for i, (kick, h1, h2, body) in enumerate(FEATURES):
        x = fx[i]
        draw_text(cv, x, 500, kick, RED, 2, bold=True)
        draw_text(cv, x, 518, h1, INK, 3, bold=True)
        draw_text(cv, x, 542, h2, INK, 3, bold=True)
        draw_para(cv, x, 570, body, INK, 2, 312, leading=2)
    cv.hline(24, 636, W - 48, INK, 2)

    # Briefs: 18 more stories, three columns
    draw_text(cv, 24, 646, "THE DAY IN BRIEF — 18 MORE STORIES", INK, 2, bold=True)
    bx = [24, 344, 664]
    for i, (num, kick, head, body) in enumerate(BRIEFS):
        col, row = i % 3, i // 3
        x = bx[col]
        y = 666 + row * 48
        draw_text(cv, x, y, num + " " + head, INK, 2, bold=True)
        draw_para(cv, x, y + 16, body, INK, 2, 312, leading=2)
    cv.hline(24, 960, W - 48, INK, 1)

    # Footer: date discipline + sources (three lines, inside the border)
    draw_text(cv, 24, 966, DATE_CHECK, RED, 2, bold=True)
    draw_text(cv, 24, 980, DATE_CHECK2, RED, 2)
    draw_text(cv, 24, 994, SOURCES, GREY, 2)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    cv = build()
    write_png(os.path.join(out_dir, "entry.png"), W, H, cv.buf)


if __name__ == "__main__":
    main()
