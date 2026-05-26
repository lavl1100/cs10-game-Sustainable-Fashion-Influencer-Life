"""
FASHIONISTA — Grow Your Platform
Kawaii desktop OS aesthetic — pastel windows, polka dots, heart decorations.

Install:  pip install arcade
Run:      python social_sim.py

Controls:
  Space   — Open compose menu      ESC — Close compose menu
  1-5     — Pick post type         Scroll / Arrow keys — Scroll feed
"""

import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import List
from enum import Enum

import arcade

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
UI_FONT_PATH = ":resources:/fonts/ttf/Kenney/Kenney_Future_Narrow.ttf"
UI_FONT_NAME = "Kenney Future Narrow"
TUTORIAL_BUBBLE_PATH = ASSETS_DIR / "speech_bubble.png"
TUTORIAL_SPRITE_PATH = ASSETS_DIR / "sprite_happy.png"

arcade.load_font(UI_FONT_PATH)

# ── Window ────────────────────────────────────────────────────────────────────
W, H  = 1100, 720
TITLE = "FASHIONISTAS ♡"
SB_W  = 285
FX    = SB_W + 14
FW    = W - SB_W - 22

# ── Kawaii palette ────────────────────────────────────────────────────────────
BG         = (255, 234, 244)   # baby pink background
BG_DOT     = (255, 214, 232)   # polka dot tint
WIN_BODY   = (255, 255, 255)   # window interior white
BORDER     = (235, 185, 210)   # default soft pink border
TEXT_DARK  = (108,  72,  92)   # dark rose — main text
TEXT_MED   = (178, 148, 163)   # medium — labels
TEXT_LITE  = (218, 194, 208)   # light — hints/dividers
WHITE      = (255, 255, 255)
BLUSH      = (255, 210, 228)
GOLD       = (255, 200,  70)   # star fill
GOLD_LITE  = (255, 230, 140)   # star empty

# Title-bar colours per post type  (bar_fill, border, dot_color)
BAR_PINK   = ((255, 178, 210), (225, 148, 180), (255, 255, 255))
BAR_BLUE   = ((185, 218, 248), (155, 188, 220), (255, 255, 255))
BAR_MINT   = ((185, 238, 218), (155, 208, 188), (255, 255, 255))
BAR_LAV    = ((218, 198, 250), (188, 168, 222), (255, 255, 255))
BAR_PEACH  = ((255, 212, 188), (225, 182, 158), (255, 255, 255))

# Button pink
BTN_FILL   = (255, 160, 198)
BTN_BORDER = (225, 125, 165)
BTN_TEXT   = (255, 255, 255)

# Sidebar stripes
SB_STRIPE_A = (255, 248, 252)
SB_STRIPE_B = (255, 238, 247)


class TutorialGuide:
    def __init__(self):
        self.bubble = arcade.Sprite(str(TUTORIAL_BUBBLE_PATH))
        self.bubble.center_x = W - 250
        self.bubble.center_y = 125
        self.bubble.width = 430
        self.bubble.height = 170
        self.sprite = arcade.Sprite(str(TUTORIAL_SPRITE_PATH))
        self.sprite.center_x = W - 78
        self.sprite.center_y = 60
        self.sprite.width = 120
        self.sprite.height = 120
        self.text = arcade.Text(
            "Choose a post type, then press the matching number key to create content and grow your audience.",
            self.bubble.center_x,
            self.bubble.center_y + 10,
            TEXT_DARK,
            14,
            font_name=UI_FONT_NAME,
            width=340,
            align="center",
            anchor_x="center",
            anchor_y="center",
            multiline=True,
        )

    def draw(self):
        self.bubble.draw()
        self.text.draw()
        self.sprite.draw()


# ── Text cache (arcade 4.x — avoid draw_text PerformanceWarning) ──────────────
class _TB:
    def __init__(self):
        self._c: dict[str, arcade.Text] = {}
        self._n: dict[str, int] = {}
        self._u: set[str] = set()

    def begin(self):
        self._n.clear(); self._u.clear()

    def draw(self, scope, text, x, y, color, size=12, bold=False, ax="left", ay="top"):
        i   = self._n.get(scope, 0); self._n[scope] = i + 1
        key = f"{scope}/{i}"; text = str(text)
        color = color if len(color) == 4 else (*color, 255)
        self._u.add(key)
        if key not in self._c:
            self._c[key] = arcade.Text(text, x, y, color,
                                       font_size=size, bold=bold,
                                       font_name=UI_FONT_NAME,
                                       anchor_x=ax, anchor_y=ay)
        else:
            t = self._c[key]
            if t.text  != text:  t.text  = text
            if t.x     != x:     t.x     = x
            if t.y     != y:     t.y     = y
            if t.color != color: t.color = color
        self._c[key].draw()

    def end(self):
        for k in set(self._c) - self._u: del self._c[k]

TB = _TB()
def txt(scope, text, x, y, color, size=12, bold=False, ax="left", ay="top"):
    TB.draw(scope, text, x, y, color, size, bold, ax, ay)


# ── Drawing primitives ────────────────────────────────────────────────────────
def rect(x, y, w, h, color):
    arcade.draw_lbwh_rectangle_filled(x, y, w, h, color)

def rect_out(x, y, w, h, color, lw=1):
    arcade.draw_lbwh_rectangle_outline(x, y, w, h, color, lw)

def hline(x1, x2, y, color=None):
    arcade.draw_line(x1, y, x2, y, color or TEXT_LITE, 1)

def pill(x, y, w, h, fill, border):
    """Approximate pill: filled rect + rounded caps via circles."""
    r = h // 2
    rect(x + r, y, w - r * 2, h, fill)
    for cx in (x + r, x + w - r):
        arcade.draw_circle_filled(cx, y + r, r, fill)
    arcade.draw_circle_outline(x + r,     y + r, r, border, 1)
    arcade.draw_circle_outline(x + w - r, y + r, r, border, 1)
    arcade.draw_line(x + r, y,     x + w - r, y,     border, 1)
    arcade.draw_line(x + r, y + h, x + w - r, y + h, border, 1)

def lerp_c(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def kawaii_window(x, y, w, h, bar_color, border_color, dot_color, bar_h=22):
    """Draw a kawaii OS-style window: coloured title bar + white body."""
    # Drop shadow
    rect(x + 3, y - 3, w, h, (*TEXT_LITE, 80))
    # White body
    rect(x, y, w, h - bar_h, WIN_BODY)
    # Title bar
    rect(x, y + h - bar_h, w, bar_h, bar_color)
    # Outer border
    rect_out(x, y, w, h, border_color, 2)
    # Inner border between bar and body
    arcade.draw_line(x, y + h - bar_h, x + w, y + h - bar_h, border_color, 1)
    # Dots (3 small circles, like window control buttons)
    dot_y = y + h - bar_h // 2
    for di in range(3):
        dx = x + 10 + di * 13
        arcade.draw_circle_filled(dx, dot_y, 4, dot_color)
        arcade.draw_circle_outline(dx, dot_y, 4, border_color, 1)

def polka_dots():
    """Draw a subtle polka-dot pattern on the background."""
    spacing = 38
    r = 4
    cols = W // spacing + 2
    rows = H // spacing + 2
    for row in range(rows):
        for col in range(cols):
            # offset every other row
            ox = (col * spacing) + (spacing // 2 if row % 2 else 0)
            oy = row * spacing
            arcade.draw_circle_filled(ox, oy, r, BG_DOT)


# ── Post Types ────────────────────────────────────────────────────────────────
class PT(Enum):
    #                label        bar        viral  growth  age   desc                                          eco_pts
    OOTD     = ("OOTD",     BAR_LAV,   0.15, 0.20,  80, "Thrifted look — reliable reach, steady growth",    1)
    HAUL     = ("HAUL",     BAR_BLUE,  0.18, 0.25, 120, "Thrift haul video — high effort, great if it lands", 2)
    TUTORIAL = ("TUTORIAL", BAR_MINT,  0.10, 0.18, 110, "Upcycle guide — builds trust over time",            4)
    ARTICLE  = ("ARTICLE",  BAR_PINK,  0.06, 0.12, 150, "Deep dive on fast fashion — slow burn, lasts longest", 5)
    REVIEW   = ("REVIEW",   BAR_PEACH, 0.20, 0.15,  90, "Sustainable brand spotlight — mid effort, good reach", 2)

    def __init__(self, label, bar, viral_chance, base_growth, max_age, desc, eco_pts):
        self.label        = label
        self.bar          = bar          # (fill, border, dot) tuple
        self.viral_chance = viral_chance
        self.base_growth  = base_growth
        self.max_age      = max_age
        self.desc         = desc
        self.eco_pts      = eco_pts      # how much this post type raises eco impact

    @property
    def color(self):   return self.bar[0]
    @property
    def border(self):  return self.bar[1]


TEMPLATES: dict = {
    PT.OOTD:     [
        "thrifted this whole look for $12 and i'm obsessed ♡",
        "op-shop haul → today's outfit, styled three ways",
        "got complimented on this coat... it's thrifted ♡",
        "slow fashion OOTD: quality over quantity always",
        "vintage blazer find and i will never shut up about it",
        "capsule wardrobe moment — one base, five fits",
        "she who thrifts well, lives well ♡",
    ],
    PT.HAUL:     [
        "come thrifting with me! everything under $20",
        "full op-shop haul: 8 pieces, $35 total",
        "charity shop finds → styled looks (no fast fashion!)",
        "thrift flip: before and after this charity shop jacket",
        "slow fashion haul — only secondhand, only sustainable",
        "weekend thrift run: what i found and what i left behind",
    ],
    PT.TUTORIAL: [
        "how i turned an old men's shirt into a crop top",
        "upcycling jeans: 5 diy ideas that actually work",
        "mending 101: make your clothes last way longer",
        "no-sew clothing repair tutorial (beginner friendly!)",
        "transforming a thrifted piece with simple embroidery",
        "dyeing faded clothes back to life — step by step",
    ],
    PT.ARTICLE:  [
        "the real cost of a $5 t-shirt (it's not $5)",
        "why fast fashion is a climate crisis — the numbers",
        "building a capsule wardrobe on a real budget",
        "what 'sustainable fashion' actually means (and what it doesn't)",
        "how to shop secondhand like a pro: a full guide",
        "the true environmental cost of textile waste",
    ],
    PT.REVIEW:   [
        "honest review: is this ethical denim brand worth it?",
        "i investigated that 'eco' label — here's what i found",
        "thrift vs. fast fashion: a real side-by-side comparison",
        "tried a clothing rental service for a month — thoughts",
        "five sustainable brands actually worth your money ♡",
        "greenwashing exposed: what to look out for when shopping",
    ],
}

MILESTONES = [
    (500,     "New Voice",        "your sustainability journey starts here ♡"),
    (1_000,   "Eco Starter",      "people are listening — keep going ♡"),
    (5_000,   "Conscious Creator","your message is spreading ♡"),
    (10_000,  "Thrift Queen",     "10K people choose slower fashion ♡"),
    (50_000,  "Sustainability Icon", "the industry is paying attention ♡"),
    (100_000, "CHANGE MAKER",     "you shifted the conversation. legendary. ♡"),
]


# ── Data classes ──────────────────────────────────────────────────────────────
@dataclass
class Post:
    ptype: PT
    text: str
    quality: float
    likes: int = 0; shares: int = 0; comments: int = 0
    age: float = 0.0; is_viral: bool = False
    viral_mult: float = 1.0; viral_flash: float = 0.0; dead: bool = False

    @property
    def engagement(self): return self.likes + self.shares * 3 + self.comments * 2
    @property
    def follower_rate(self): return self.engagement * self.quality * self.viral_mult * 0.004

    def tick(self, dt):
        self.age += dt
        if self.age >= self.ptype.max_age: self.dead = True; return
        decay = max(0.05, 1.0 - self.age / self.ptype.max_age)
        rate  = self.ptype.base_growth * self.quality * decay * self.viral_mult
        if random.random() < rate * dt:
            self.likes    += random.randint(1, 15)
            self.shares   += random.randint(0,  4)
            self.comments += random.randint(0,  5)
        if self.viral_flash > 0: self.viral_flash = max(0.0, self.viral_flash - dt)

@dataclass
class Notif:
    text: str; timer: float; color: tuple


# ── Main window ───────────────────────────────────────────────────────────────
class Fashionista(arcade.Window):
    CARD_H  = 148
    BAR_H   = 22      # window title bar height
    SB_BAR  = 26      # sidebar header bar height

    def __init__(self):
        super().__init__(W, H, TITLE)
        arcade.set_background_color(BG)
        self.followers = 100;  self.day = 1
        self.day_timer = 0.0;  self.day_len = 60.0
        self.energy = 10;      self.max_energy = 10
        self.posts_made = 0;   self.viral_count = 0
        self.eco_impact = 0;   self.total_likes = 0
        self.milestone_idx = 0
        self._fol_frac = 0.0
        self.posts: List[Post] = []
        self.notifs: List[Notif] = []
        self.post_types: List[PT] = list(PT)
        self.scroll = 0;  self.composing = False;  self.hover_idx = -1
        self.tutorial_guide = TutorialGuide()

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _gain(self, n):
        self.followers += n
        while self.milestone_idx < len(MILESTONES):
            thr, title, sub = MILESTONES[self.milestone_idx]
            if self.followers < thr: break
            self._notif(f"♡  {title} — {sub}", GOLD)
            self.milestone_idx += 1; self.max_energy = min(20, self.max_energy + 2)

    def _notif(self, text, color=TEXT_DARK):
        self.notifs.append(Notif(text, 3.5, color))
        if len(self.notifs) > 6: self.notifs.pop(0)

    # ── Update ────────────────────────────────────────────────────────────────
    def on_update(self, dt):
        dt = min(dt, 0.1)
        self.day_timer += dt
        if self.day_timer >= self.day_len:
            self.day_timer -= self.day_len; self.day += 1
            self.energy = self.max_energy
            self._notif(f"Day {self.day} ♡ energy restored!", BTN_FILL)

        total_rate = 0.0
        for p in self.posts:
            p.tick(dt)
            if p.dead: continue
            if not p.is_viral and random.random() < p.ptype.viral_chance * dt:
                p.is_viral = True; p.viral_mult = random.uniform(3.0, 9.0)
                p.viral_flash = 2.5; self.viral_count += 1
                self._notif(f"♡  {p.ptype.label} went VIRAL! ({p.viral_mult:.1f}x)", GOLD)
            total_rate += p.follower_rate

        self._fol_frac += total_rate * dt
        if self._fol_frac >= 1.0:
            g = int(self._fol_frac); self._fol_frac -= g; self._gain(g)

        if not self.posts and random.random() < 0.0005:
            self.followers = max(0, self.followers - 1)
        self.posts = [p for p in self.posts if not p.dead]
        self.total_likes = sum(p.likes for p in self.posts)
        for n in self.notifs: n.timer -= dt
        self.notifs = [n for n in self.notifs if n.timer > 0]

    # ── Post creation ─────────────────────────────────────────────────────────
    def _create_post(self, ptype):
        if self.energy <= 0:
            self._notif("No energy left — wait for tomorrow ♡", BTN_BORDER); return
        skill   = min(0.8, math.log10(max(10, self.followers)) / 6.0)
        quality = max(0.05, min(1.0, random.betavariate(1.0 + skill * 3, max(1.2, 4.0 - skill * 2))))
        post = Post(ptype=ptype, text=random.choice(TEMPLATES[ptype]), quality=quality)
        self.posts.insert(0, post); self.posts = self.posts[:20]
        self.posts_made += 1; self.energy -= 1; self.scroll = 0
        self.eco_impact += ptype.eco_pts
        qlabel = "serving sustainability ♡" if quality > 0.70 else "pretty decent ♡" if quality > 0.40 else "a little weak..."
        self._notif(f"Posted  |  {qlabel}  ({quality:.0%})",
                    BAR_MINT[0] if quality > 0.70 else GOLD if quality > 0.40 else BAR_PEACH[1])
        self.composing = False

    # ── Drawing ───────────────────────────────────────────────────────────────
    def on_draw(self):
        TB.begin()
        self.clear()
        polka_dots()
        self._draw_sidebar()
        self._draw_feed()
        self._draw_notifs()
        if self.composing: self._draw_compose()
        self.tutorial_guide.draw()
        TB.end()

    # ── Sidebar ───────────────────────────────────────────────────────────────
    def _draw_sidebar(self):
        # Striped sidebar body
        sw = 14
        for i in range(SB_W // sw + 1):
            rect(i * sw, 0, sw, H, SB_STRIPE_A if i % 2 == 0 else SB_STRIPE_B)
        # Window chrome
        kawaii_window(8, 8, SB_W - 16, H - 16, BAR_PINK[0], BAR_PINK[1], BAR_PINK[2], self.SB_BAR)

        S = "sb"
        # Title in bar
        txt(S, "FASHIONISTAS ♡", SB_W // 2, H - 8 - self.SB_BAR // 2,
            TEXT_DARK, 9, bold=True, ax="center", ay="center")

        y = H - 16 - self.SB_BAR - 18

        # Followers (inside a blush pill)
        f    = self.followers
        fstr = (f"{f/1_000_000:.1f}M" if f >= 1_000_000
                else f"{f/1_000:.1f}K"  if f >= 1_000 else str(f))
        txt(S, "followers", SB_W // 2, y, TEXT_MED, 9, ax="center")
        y -= 14
        txt(S, fstr, SB_W // 2, y, TEXT_DARK, 34, bold=True, ax="center")
        y -= 40

        hline(30, SB_W - 30, y, TEXT_LITE)
        y -= 14

        # Day + progress pill
        season   = (self.day - 1) // 7 + 1
        day_in_s = (self.day - 1) % 7 + 1
        txt(S, f"Season {season}  ♡  Day {day_in_s}", SB_W // 2, y, TEXT_MED, 9, ax="center")
        y -= 14
        pw = SB_W - 60
        px = 30
        # pill track
        pill(px, y - 8, pw, 10, BLUSH, BORDER)
        # pill fill
        prog = self.day_timer / self.day_len
        if prog > 0.05:
            fill_w = max(10, int(pw * prog))
            pill(px, y - 8, fill_w, 10, BTN_FILL, BTN_BORDER)
        y -= 26

        hline(30, SB_W - 30, y, TEXT_LITE)
        y -= 14

        # Energy hearts
        txt(S, "energy", SB_W // 2, y, TEXT_MED, 9, ax="center")
        y -= 16
        pip_w = min(18, (SB_W - 60) / max(1, self.max_energy))
        total_pip = pip_w * self.max_energy
        start_x   = SB_W // 2 - total_pip // 2
        for i in range(self.max_energy):
            cx = start_x + (i + 0.5) * pip_w
            c  = BTN_FILL if i < self.energy else (*BLUSH, 255)
            arcade.draw_circle_filled(cx, y - 5, 6, c)
            arcade.draw_circle_outline(cx, y - 5, 6, BTN_BORDER, 1)
        y -= 26

        hline(30, SB_W - 30, y, TEXT_LITE)
        y -= 16

        # Stats
        for label, val in [
            ("posts made",   str(self.posts_made)),
            ("eco impact",   str(self.eco_impact)),
            ("active posts", str(len(self.posts))),
            ("total likes",  f"{self.total_likes:,}"),
        ]:
            txt(S, label, 28,        y, TEXT_MED,  10)
            txt(S, val,   SB_W - 28, y, TEXT_DARK, 10, bold=True, ax="right")
            y -= 22

        hline(30, SB_W - 30, y, TEXT_LITE)

        # POST button — pink pill
        bw, bh = SB_W - 48, 36
        bx = 24; by = 24
        pill(bx, by, bw, bh, BTN_FILL, BTN_BORDER)
        txt(S, "♡  POST  ♡", SB_W // 2, by + bh // 2 + 1, WHITE, 13, bold=True, ax="center", ay="center")
        txt(S, "Space or click here", SB_W // 2, 10, TEXT_LITE, 8, ax="center")

    # ── Feed ──────────────────────────────────────────────────────────────────
    def _draw_feed(self):
        txt("feed", "♡  your feed", FX + 4, H - 16, TEXT_MED, 10, bold=True)
        hline(FX, W - 10, H - 28, TEXT_LITE)

        if not self.posts:
            txt("feed", "nothing posted yet ♡",                        FX + FW//2, H//2+18, TEXT_MED, 15, ax="center")
            txt("feed", "press Space to share your first sustainable post", FX + FW//2, H//2-4, TEXT_MED, 11, ax="center")
            return

        y = H - 44 + self.scroll
        for slot, post in enumerate(self.posts):
            ch = self.CARD_H
            if y - ch > H + 5: y -= ch + 10; continue
            if y < -10: break
            self._draw_card(post, FX + 2, y - ch, FW - 4, ch, slot)
            y -= ch + 10

    def _draw_card(self, post: Post, x, y, w, h, slot: int):
        S   = f"c{slot}"
        bar = post.ptype.bar          # (fill, border, dot)
        bh  = self.BAR_H

        # Viral: flash body between white and bar tint
        if post.viral_flash > 0:
            t  = (post.viral_flash % 0.4) / 0.4
            body_bg = lerp_c(WIN_BODY, bar[0], t * 0.3)
        else:
            body_bg = WIN_BODY

        kawaii_window(x, y, w, h, bar[0], bar[1], bar[2], bh)
        # Override body bg when viral
        if body_bg != WIN_BODY:
            rect(x + 2, y + 1, w - 4, h - bh - 2, body_bg)

        # Post type label in title bar
        txt(S, post.ptype.label, x + w // 2, y + h - bh // 2,
            TEXT_DARK, 10, bold=True, ax="center", ay="center")

        # Viral pill in title bar (right side) OR invisible placeholder
        if post.is_viral:
            pill(x + w - 68, y + h - bh + 4, 60, bh - 8, GOLD, (200, 160, 50))
            txt(S, "♡ VIRAL", x + w - 38, y + h - bh // 2,
                TEXT_DARK, 8, bold=True, ax="center", ay="center")
        else:
            txt(S, "", 0, 0, (*TEXT_DARK, 0), 1)   # stable placeholder

        # Post text
        short = post.text[:68] + ("..." if len(post.text) > 68 else "")
        txt(S, short, x + 12, y + h - bh - 16, TEXT_DARK, 12)

        # Quality stars  ★★★☆☆
        stars = max(1, round(post.quality * 5))
        star_str = "★" * stars + "☆" * (5 - stars)
        txt(S, star_str, x + 12, y + h - bh - 38, GOLD, 12)

        # Divider
        hline(x + 10, x + w - 10, y + 50, BLUSH)

        # Engagement
        txt(S, f"♡ {post.likes:,}",  x + 14,        y + 34, TEXT_MED, 11)
        txt(S, f"↺ {post.shares:,}", x + 14 + 95,   y + 34, TEXT_MED, 11)
        txt(S, f"✉ {post.comments:,}", x + 14 + 190, y + 34, TEXT_MED, 11)

        # Lifetime bar — thin pill at bottom of card, below engagement
        remaining = max(0.0, 1.0 - post.age / post.ptype.max_age)
        track_w   = w - 24
        pill(x + 12, y + 8, track_w, 8, BLUSH, TEXT_LITE)
        if remaining > 0.02:
            fill_w = max(8, int(track_w * remaining))
            fill_c = lerp_c(BAR_PEACH[1], bar[0], remaining)
            pill(x + 12, y + 8, fill_w, 8, fill_c, bar[1])

    # ── Compose overlay ───────────────────────────────────────────────────────
    def _draw_compose(self):
        # Soft blush overlay
        arcade.draw_lbwh_rectangle_filled(0, 0, W, H, (*BLUSH, 180))

        mw, mh = 650, 468
        mx = W // 2 - mw // 2
        my = H // 2 - mh // 2

        # Dialog window
        kawaii_window(mx, my, mw, mh, BAR_PINK[0], BAR_PINK[1], BAR_PINK[2], 28)

        txt("cmp", "♡  what are you creating today?  ♡",
            W // 2, my + mh - 14, TEXT_DARK, 13, bold=True, ax="center", ay="center")
        txt("cmp", "click a button  or  press 1–5  ♡  ESC to cancel",
            W // 2, my + mh - 40, TEXT_MED, 9, ax="center")

        n       = len(self.post_types)
        btn_h   = 58
        gap     = 8
        total   = n * btn_h + (n - 1) * gap
        start_y = my + mh - 70 - total

        for i, pt in enumerate(self.post_types):
            S   = f"cb{i}"
            bx  = mx + 18
            by  = start_y + (n - 1 - i) * (btn_h + gap)
            bw  = mw - 36
            bar = pt.bar
            hover = (self.hover_idx == i)

            # Card window per post type
            kawaii_window(bx, by, bw, btn_h, bar[0], bar[1], bar[2], 20)
            if hover:
                rect_out(bx, by, bw, btn_h, bar[1], 3)

            # Number key badge
            arcade.draw_circle_filled(bx + 28, by + btn_h // 2, 13, bar[0])
            arcade.draw_circle_outline(bx + 28, by + btn_h // 2, 13, bar[1], 1)
            txt(S, str(i + 1), bx + 28, by + btn_h // 2 + 1,
                TEXT_DARK, 13, bold=True, ax="center", ay="center")

            # Label + description
            txt(S, pt.label,
                bx + 50, by + btn_h - 20 - 4, TEXT_DARK, 12, bold=True)
            txt(S, f"viral: {pt.viral_chance:.0%}  ♡  growth: {pt.base_growth:.0%}"
                   f"  ♡  lifetime: {pt.max_age}s  ♡  {pt.desc}",
                bx + 50, by + 10, TEXT_MED, 9)

    # ── Notifications (kawaii speech-bubble style) ────────────────────────────
    def _draw_notifs(self):
        y = 80
        for i, n in enumerate(reversed(self.notifs[-5:])):
            alpha    = int(min(1.0, n.timer) * 255)
            bg_alpha = int(min(1.0, n.timer) * 210)
            tw       = len(n.text) * 7 + 28
            # Pill background
            pill(W - tw - 14, y - 5, tw, 22, (*BLUSH, bg_alpha), (*BORDER, bg_alpha))
            txt(f"ntf{i}", n.text, W - 16, y, (*n.color[:3], alpha), 11, ax="right")
            y += 28

    # ── Input ─────────────────────────────────────────────────────────────────
    def on_key_press(self, key, mod):
        if key == arcade.key.ESCAPE:   self.composing = False; return
        if key == arcade.key.SPACE and not self.composing: self.composing = True; return
        if self.composing:
            m = {arcade.key.KEY_1:0, arcade.key.KEY_2:1, arcade.key.KEY_3:2,
                 arcade.key.KEY_4:3, arcade.key.KEY_5:4}
            if key in m and m[key] < len(self.post_types):
                self._create_post(self.post_types[m[key]])
            return
        if key == arcade.key.UP:   self.scroll = max(0, self.scroll - 100)
        elif key == arcade.key.DOWN: self.scroll = min(len(self.posts)*(self.CARD_H+10), self.scroll+100)

    def on_mouse_press(self, x, y, button, mod):
        if self.composing:
            idx = self._chit(x, y)
            if idx >= 0: self._create_post(self.post_types[idx])
        else:
            if 24 <= x <= SB_W - 24 and 24 <= y <= 60: self.composing = True

    def on_mouse_motion(self, x, y, dx, dy):
        self.hover_idx = self._chit(x, y) if self.composing else -1

    def on_mouse_scroll(self, x, y, sx, sy):
        self.scroll = max(0, self.scroll - int(sy * 35))

    def _chit(self, x, y):
        mw, mh  = 650, 468
        mx      = W // 2 - mw // 2
        my      = H // 2 - mh // 2
        n       = len(self.post_types)
        btn_h, gap = 58, 8
        total   = n * btn_h + (n - 1) * gap
        start_y = my + mh - 70 - total
        for i in range(n):
            bx = mx + 18; bw = mw - 36
            by = start_y + (n - 1 - i) * (btn_h + gap)
            if bx <= x <= bx + bw and by <= y <= by + btn_h: return i
        return -1


if __name__ == "__main__":
    game = Fashionista()
    arcade.run()
