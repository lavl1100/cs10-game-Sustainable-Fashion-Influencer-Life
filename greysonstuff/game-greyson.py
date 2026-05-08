"""
SocialSim — Grow Your Platform
A social media simulation game built with Python + Arcade.

Install:  pip install arcade
Run:      python social_sim.py

Controls:
  Space       — Open compose menu
  1-5         — Quick-pick post type while compose menu is open
  ESC         — Close compose menu
  Scroll      — Scroll the feed
  Click       — Compose button in sidebar / post type buttons
"""

import math
import random
from dataclasses import dataclass
from typing import List
from enum import Enum

import arcade

# ── Window ────────────────────────────────────────────────────────────────────
W, H  = 1100, 720
TITLE = "SocialSim — Grow Your Platform"

SB_W = 280          # sidebar width
FX   = SB_W + 10    # feed area left edge
FW   = W - SB_W - 20  # feed area width

# ── Palette ───────────────────────────────────────────────────────────────────
BG       = (12,  12,  22)
PANEL    = (20,  22,  38)
CARD     = (28,  30,  50)
CARD_VIR = (50,  30,   8)
BLUE     = (70, 150, 255)
GREEN    = (70, 210, 100)
RED      = (255, 85,  85)
GOLD     = (255, 195, 55)
PURPLE   = (175, 85, 255)
ORANGE   = (255, 145, 30)
WHITE    = (235, 235, 245)
GRAY     = (140, 140, 165)
DGRAY    = (55,  55,  80)
BLACK    = (0,   0,   0)


# ── Colour helpers ────────────────────────────────────────────────────────────

def lerp_c(a, b, t):
    """Linearly interpolate between two RGB tuples."""
    t = max(0.0, min(1.0, t))
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


# ── Drawing helpers (bottom-left origin) ──────────────────────────────────────

def rect(x, y, w, h, color):
    arcade.draw_lbwh_rectangle_filled(x, y, w, h, color)


def rect_out(x, y, w, h, color, lw=1):
    arcade.draw_lbwh_rectangle_outline(x, y, w, h, color, lw)


def txt(text, x, y, color, size=13, bold=False, ax="left", ay="top"):
    arcade.draw_text(str(text), x, y, color, size, bold=bold,
                     anchor_x=ax, anchor_y=ay)


# ── Post Types ────────────────────────────────────────────────────────────────

class PT(Enum):
    """Post type enum — each value packs all stats."""
    # name         label       icon  color   viral  growth  max_age  desc
    MEME     = ("Meme",     "MEM", PURPLE, 0.30,  0.18,   90,   "Funny & shareable — high viral shot, short shelf life")
    VIDEO    = ("Video",    "VID", RED,    0.20,  0.25,  120,   "High effort, great growth if it lands")
    ARTICLE  = ("Article",  "ART", BLUE,   0.08,  0.12,  150,   "Slow burn — low viral, longest lasting")
    SELFIE   = ("Selfie",   "SEL", GREEN,  0.12,  0.20,   80,   "Reliable likes, rarely breaks through")
    HOT_TAKE = ("Hot Take", "HOT", ORANGE, 0.45,  0.08,   60,   "Chaotic — highest viral chance, polarising")

    def __init__(self, label, icon, color, viral_chance, base_growth, max_age, desc):
        self.label        = label
        self.icon         = icon
        self.color        = color
        self.viral_chance = viral_chance   # prob/s of going viral
        self.base_growth  = base_growth    # engagement events/s (base)
        self.max_age      = max_age        # seconds before post expires
        self.desc         = desc


TEMPLATES: dict = {
    PT.MEME: [
        "When Monday hits different 💀",
        "This is fine. 🔥",
        "POV: you're the main character",
        "Day {n}: still haven't touched grass",
        "Nobody:\nMe at 3am: *opens laptop*",
        "Real ones remember when internet was simple",
        "I'm not like other accounts (I am)",
    ],
    PT.VIDEO: [
        "I only ate pizza for a week (honest review)",
        "24 hours in the world's smallest apartment",
        "Teaching grandma to speedrun Minecraft",
        "Built a gaming PC completely blindfolded",
        "Trying every menu item at McDonald's",
        "Reacting to my oldest cringe videos",
    ],
    PT.ARTICLE: [
        "5 things nobody tells you about freelancing",
        "Why I quit my 6-figure job (full story)",
        "The hidden cost of productivity culture",
        "AI won't replace developers. Here's why.",
        "Your morning routine is lying to you",
        "The economics of going viral, explained",
    ],
    PT.SELFIE: [
        "Finally got a haircut ✂️",
        "Golden hour hit different today 🌅",
        "New chapter, new vibe ✨",
        "First day energy 🎉",
        "Road trip + good vibes only 🚗",
        "New fit, who dis 👀",
    ],
    PT.HOT_TAKE: [
        "Unpopular opinion: pineapple belongs on pizza",
        "Hustle culture is a scam. I said it.",
        "Dogs > cats. Not debatable.",
        "Open offices completely destroyed productivity",
        "Mornings are actually terrible. Change my mind.",
        "Cold brew is just overpriced cold coffee",
    ],
}

MILESTONES = [500, 1_000, 5_000, 10_000, 50_000, 100_000]


# ── Data classes ──────────────────────────────────────────────────────────────

@dataclass
class Post:
    ptype: PT
    text: str
    quality: float          # 0..1, rolled at creation time

    likes: int    = 0
    shares: int   = 0
    comments: int = 0

    age: float         = 0.0
    is_viral: bool     = False
    viral_mult: float  = 1.0
    viral_flash: float = 0.0   # countdown for glow animation
    dead: bool         = False

    @property
    def engagement(self):
        return self.likes + self.shares * 3 + self.comments * 2

    @property
    def follower_rate(self):
        """Followers accumulated per second while this post is alive."""
        return self.engagement * self.quality * self.viral_mult * 0.004

    def tick(self, dt: float):
        self.age += dt
        if self.age >= self.ptype.max_age:
            self.dead = True
            return

        # Engagement decays toward the post's natural death
        decay     = max(0.05, 1.0 - self.age / self.ptype.max_age)
        rate      = self.ptype.base_growth * self.quality * decay * self.viral_mult

        # Stochastic engagement tick — heart of the probability system
        if random.random() < rate * dt:
            self.likes    += random.randint(1, 15)
            self.shares   += random.randint(0,  4)
            self.comments += random.randint(0,  5)

        if self.viral_flash > 0:
            self.viral_flash = max(0.0, self.viral_flash - dt)


@dataclass
class Notif:
    text:  str
    timer: float
    color: tuple


# ── Main game window ──────────────────────────────────────────────────────────

class SocialSim(arcade.Window):

    CARD_H = 130   # pixels per feed card

    def __init__(self):
        super().__init__(W, H, TITLE)
        arcade.set_background_color(BG)

        # ── Game state ────────────────────────────────────────────────────────
        self.followers:    int   = 100
        self.day:          int   = 1
        self.day_timer:    float = 0.0
        self.day_len:      float = 60.0   # real seconds per in-game day
        self.energy:       int   = 10
        self.max_energy:   int   = 10
        self.posts_made:   int   = 0
        self.viral_count:  int   = 0
        self.total_likes:  int   = 0
        self.milestone_idx: int  = 0
        self._fol_frac:    float = 0.0    # sub-integer accumulator

        self.posts:      List[Post]  = []
        self.notifs:     List[Notif] = []
        self.post_types: List[PT]    = list(PT)

        self.scroll:    int  = 0
        self.composing: bool = False
        self.hover_idx: int  = -1

    # ── Follower helpers ──────────────────────────────────────────────────────

    def _gain_followers(self, n: int):
        self.followers += n
        while (self.milestone_idx < len(MILESTONES) and
               self.followers >= MILESTONES[self.milestone_idx]):
            m     = MILESTONES[self.milestone_idx]
            label = f"{m // 1_000}K" if m >= 1_000 else str(m)
            self._notif(f"🎉  {label} followers!  Keep posting!", GOLD)
            self.milestone_idx += 1
            self.max_energy = min(20, self.max_energy + 2)

    def _notif(self, text, color=WHITE):
        self.notifs.append(Notif(text, 3.5, color))
        if len(self.notifs) > 6:
            self.notifs.pop(0)

    # ── Update ────────────────────────────────────────────────────────────────

    def on_update(self, dt):
        dt = min(dt, 0.1)

        # ── Day cycle ─────────────────────────────────────────────────────────
        self.day_timer += dt
        if self.day_timer >= self.day_len:
            self.day_timer -= self.day_len
            self.day       += 1
            self.energy     = self.max_energy
            self._notif(f"Day {self.day} begins!  Energy fully restored.", BLUE)

        # ── Tick each active post ─────────────────────────────────────────────
        total_rate = 0.0
        for p in self.posts:
            p.tick(dt)
            if p.dead:
                continue

            # Viral roll — each second there is a ptype.viral_chance prob
            if not p.is_viral and random.random() < p.ptype.viral_chance * dt:
                p.is_viral    = True
                p.viral_mult  = random.uniform(3.0, 9.0)
                p.viral_flash = 2.5
                self.viral_count += 1
                self._notif(f"🔥  Your {p.ptype.label} went VIRAL! ({p.viral_mult:.1f}x boost)", ORANGE)

            total_rate += p.follower_rate

        # ── Accumulate followers ──────────────────────────────────────────────
        self._fol_frac += total_rate * dt
        if self._fol_frac >= 1.0:
            gained          = int(self._fol_frac)
            self._fol_frac -= gained
            self._gain_followers(gained)

        # Tiny passive decay when completely idle
        if not self.posts and random.random() < 0.0005:
            self.followers = max(0, self.followers - 1)

        # ── Cleanup ───────────────────────────────────────────────────────────
        self.posts  = [p for p in self.posts if not p.dead]
        self.total_likes = sum(p.likes for p in self.posts)

        for n in self.notifs:
            n.timer -= dt
        self.notifs = [n for n in self.notifs if n.timer > 0]

    # ── Post creation ─────────────────────────────────────────────────────────

    def _create_post(self, ptype: PT):
        if self.energy <= 0:
            self._notif("No energy left — wait for the next day!", RED)
            return

        # Quality from a beta distribution.
        # As your following grows your 'skill' improves, shifting the distribution.
        skill = min(0.8, math.log10(max(10, self.followers)) / 6.0)
        alpha = 1.0 + skill * 3.0
        beta  = max(1.2, 4.0 - skill * 2.0)
        quality = random.betavariate(alpha, beta)
        quality = max(0.05, min(1.0, quality))

        template = random.choice(TEMPLATES[ptype])
        text     = template.replace("{n}", str(self.day))

        post = Post(ptype=ptype, text=text, quality=quality)
        self.posts.insert(0, post)
        self.posts    = self.posts[:20]   # cap feed length
        self.posts_made += 1
        self.energy     -= 1
        self.scroll      = 0              # snap to top

        if quality > 0.70:
            qlabel, qc = "Great!",  GREEN
        elif quality > 0.40:
            qlabel, qc = "Decent",  GOLD
        else:
            qlabel, qc = "Weak",    RED

        self._notif(f"Posted {ptype.icon}  ·  Quality: {qlabel} ({quality:.0%})", qc)
        self.composing = False

    # ── Drawing ───────────────────────────────────────────────────────────────

    def on_draw(self):
        self.clear()
        self._draw_sidebar()
        self._draw_feed()
        self._draw_notifs()
        if self.composing:
            self._draw_compose()

    # ── Sidebar ───────────────────────────────────────────────────────────────

    def _draw_sidebar(self):
        rect(0, 0, SB_W, H, PANEL)
        arcade.draw_line(SB_W, 0, SB_W, H, DGRAY, 1)

        y = H - 18

        txt("SocialSim", 14, y, BLUE, 20, bold=True)
        y -= 36
        arcade.draw_line(10, y, SB_W - 10, y, DGRAY, 1)
        y -= 28

        # Followers counter
        f    = self.followers
        fstr = (f"{f / 1_000_000:.1f}M" if f >= 1_000_000
                else f"{f / 1_000:.1f}K" if f >= 1_000
                else str(f))
        txt("FOLLOWERS", 14, y, GRAY, 10)
        y -= 20
        txt(fstr, 14, y, WHITE, 32, bold=True)
        y -= 46

        # Day + progress bar
        txt(f"Day  {self.day}", 14, y, GRAY, 12)
        y -= 18
        bw   = SB_W - 28
        prog = self.day_timer / self.day_len
        rect(14, y - 10, bw, 10, DGRAY)
        rect(14, y - 10, int(bw * prog), 10, BLUE)
        y -= 28

        # Energy pip row
        txt("ENERGY", 14, y, GRAY, 10)
        y -= 20
        pip_w = (SB_W - 30) / max(1, self.max_energy)
        for i in range(self.max_energy):
            c = GOLD if i < self.energy else DGRAY
            arcade.draw_circle_filled(20 + (i + 0.5) * pip_w, y - 4, 6, c)
        y -= 30

        arcade.draw_line(10, y, SB_W - 10, y, DGRAY, 1)
        y -= 20

        # Stats panel
        for label, val in [
            ("Posts Made",   str(self.posts_made)),
            ("Gone Viral",   str(self.viral_count)),
            ("Active Posts", str(len(self.posts))),
            ("Total Likes",  f"{self.total_likes:,}"),
        ]:
            txt(label, 14, y, GRAY, 11)
            txt(val, SB_W - 14, y, WHITE, 12, ax="right")
            y -= 22

        y -= 14
        arcade.draw_line(10, y, SB_W - 10, y, DGRAY, 1)

        # Compose button
        bh = 44
        rect(10, 30, SB_W - 20, bh, BLUE)
        txt("+ New Post", SB_W // 2, 30 + bh - 10, WHITE, 15, bold=True, ax="center")
        txt("Space · or click here", SB_W // 2, 16, GRAY, 9, ax="center")

    # ── Feed ──────────────────────────────────────────────────────────────────

    def _draw_feed(self):
        txt("YOUR FEED", FX + 4, H - 18, GRAY, 11, bold=True)

        if not self.posts:
            txt("No posts yet — press Space to publish your first post!",
                FX + FW // 2, H // 2, GRAY, 15, ax="center")
            return

        y = H - 50 + self.scroll
        for post in self.posts:
            ch = self.CARD_H
            if y - ch > H + 5:
                y -= ch + 8
                continue
            if y < -10:
                break
            self._draw_card(post, FX + 2, y - ch, FW - 4, ch)
            y -= ch + 8

    def _draw_card(self, post: Post, x, y, w, h):
        # Background — flashes orange/dark when newly viral
        if post.viral_flash > 0:
            t  = (post.viral_flash % 0.5) / 0.5
            bg = lerp_c(CARD, CARD_VIR, t)
        else:
            bg = CARD_VIR if post.is_viral else CARD
        rect(x, y, w, h, bg)

        # Left color strip by post type
        rect(x, y, 4, h, post.ptype.color)

        # Post-type label
        txt(f"[{post.ptype.icon}] {post.ptype.label}",
            x + 12, y + h - 12, post.ptype.color, 12, bold=True)

        # Viral badge (top-right)
        if post.is_viral:
            rect(x + w - 70, y + h - 22, 64, 18, ORANGE)
            txt("VIRAL!", x + w - 38, y + h - 20, BLACK, 10, bold=True, ax="center")

        # Quality bar (coloured strip under the label)
        rect(x + 4, y + h - 4, w - 8, 4, lerp_c(RED, GREEN, post.quality))

        # Post text (truncated to one line)
        short = post.text[:68] + ("…" if len(post.text) > 68 else "")
        txt(short, x + 12, y + h - 32, WHITE, 13)

        # Engagement counters
        for i, (icon, val) in enumerate([
            ("<3", post.likes),
            ("RT", post.shares),
            ("//", post.comments),
        ]):
            txt(f"{icon} {val:,}", x + 14 + i * 90, y + 18, GRAY, 12)

        # Lifetime countdown bar (bottom of card)
        remaining = max(0.0, 1.0 - post.age / post.ptype.max_age)
        rect(x, y, w, 4, DGRAY)
        rect(x, y, int(w * remaining), 4, lerp_c(RED, BLUE, remaining))

    # ── Compose overlay ───────────────────────────────────────────────────────

    def _draw_compose(self):
        # Dim the background
        arcade.draw_lbwh_rectangle_filled(0, 0, W, H, (0, 0, 0, 170))

        mw, mh = 640, 440
        mx = W // 2 - mw // 2
        my = H // 2 - mh // 2

        rect(mx, my, mw, mh, PANEL)
        rect_out(mx, my, mw, mh, BLUE, 2)

        txt("Choose Post Type", W // 2, my + mh - 16,
            WHITE, 20, bold=True, ax="center")
        txt("click a button  or  press 1–5  ·  ESC to cancel",
            W // 2, my + mh - 40, GRAY, 11, ax="center")

        n       = len(self.post_types)
        btn_h   = 56
        gap     = 8
        total   = n * btn_h + (n - 1) * gap
        start_y = my + mh // 2 + total // 2 - 30

        for i, pt in enumerate(self.post_types):
            bx = mx + 20
            by = start_y - i * (btn_h + gap) - btn_h
            bw = mw - 40

            hover = (self.hover_idx == i)
            bg    = lerp_c(CARD, pt.color, 0.28) if hover else CARD
            rect(bx, by, bw, btn_h, bg)
            rect_out(bx, by, bw, btn_h, pt.color, 2 if hover else 1)

            txt(str(i + 1), bx + 14, by + btn_h - 14, pt.color, 18, bold=True)
            txt(f"[{pt.icon}]  {pt.label}",
                bx + 44, by + btn_h - 16, WHITE, 15, bold=True)
            txt(
                f"Viral chance: {pt.viral_chance:.0%}  ·  "
                f"Growth: {pt.base_growth:.0%}  ·  "
                f"Lifetime: {pt.max_age}s  ·  {pt.desc}",
                bx + 44, by + 10, GRAY, 10,
            )

    # ── Notifications ─────────────────────────────────────────────────────────

    def _draw_notifs(self):
        y = 85
        for n in list(reversed(self.notifs[-5:])):
            alpha = int(min(1.0, n.timer) * 255)
            c = (*n.color[:3], alpha)
            txt(n.text, W - 16, y, c, 12, ax="right")
            y += 22

    # ── Input ─────────────────────────────────────────────────────────────────

    def on_key_press(self, key, mod):
        if key == arcade.key.ESCAPE:
            self.composing = False
            return

        if key == arcade.key.SPACE and not self.composing:
            self.composing = True
            return

        if self.composing:
            mapping = {
                arcade.key.KEY_1: 0, arcade.key.KEY_2: 1, arcade.key.KEY_3: 2,
                arcade.key.KEY_4: 3, arcade.key.KEY_5: 4,
            }
            if key in mapping:
                idx = mapping[key]
                if idx < len(self.post_types):
                    self._create_post(self.post_types[idx])
            return

        if key == arcade.key.UP:
            self.scroll = max(0, self.scroll - 100)
        elif key == arcade.key.DOWN:
            self.scroll = min(len(self.posts) * (self.CARD_H + 8), self.scroll + 100)

    def on_mouse_press(self, x, y, button, mod):
        if self.composing:
            idx = self._compose_hit(x, y)
            if idx >= 0:
                self._create_post(self.post_types[idx])
        else:
            # Sidebar compose button
            if 10 <= x <= SB_W - 10 and 30 <= y <= 74:
                self.composing = True

    def on_mouse_motion(self, x, y, dx, dy):
        self.hover_idx = self._compose_hit(x, y) if self.composing else -1

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.scroll = max(0, self.scroll - int(scroll_y * 35))

    # ── Compose hit-test ──────────────────────────────────────────────────────

    def _compose_hit(self, x, y) -> int:
        mw, mh  = 640, 440
        mx      = W // 2 - mw // 2
        my      = H // 2 - mh // 2
        n       = len(self.post_types)
        btn_h   = 56
        gap     = 8
        total   = n * btn_h + (n - 1) * gap
        start_y = my + mh // 2 + total // 2 - 30

        for i in range(n):
            bx = mx + 20
            by = start_y - i * (btn_h + gap) - btn_h
            bw = mw - 40
            if bx <= x <= bx + bw and by <= y <= by + btn_h:
                return i
        return -1


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    game = SocialSim()
    arcade.run()
