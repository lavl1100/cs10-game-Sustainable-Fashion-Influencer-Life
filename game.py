from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import math
from pathlib import Path
import random
import time
import warnings
from enum import Enum
from typing import Callable, Optional

warnings.filterwarnings(
    "ignore",
    message=r"pkg_resources is deprecated as an API\.",
    module=r"pygame\.pkgdata",
)

import arcade
import pygame

BASE_SCREEN_WIDTH = 800
BASE_SCREEN_HEIGHT = 600
DEFAULT_WINDOW_WIDTH = 1280
DEFAULT_WINDOW_HEIGHT = 720
SCREEN_TITLE = "Fashion Influencer Life"

ASSETS_DIR = Path(__file__).resolve().parent / "assets"
BACKGROUND_IMAGE = ASSETS_DIR / "home_background.png"

BUTTON_IMAGE_PATHS = {
    "settings": ASSETS_DIR / "settings_button.png",
    "social media": ASSETS_DIR / "social_media_button.png",
    "closet": ASSETS_DIR / "closet_button.png",
    "clothing store": ASSETS_DIR / "clothing_store_button.png",
    "activity center": ASSETS_DIR / "activity_center_button.png",
}

BUTTON_ACTIVE_IMAGE_PATHS = {
    "social media": ASSETS_DIR / "social_media_button_active.png",
}

# Base layout values expressed in the original 800x600 design space.
SIDE_BAR_X = 64
SIDE_BAR_Y = 270
SIDE_BAR_WIDTH = 84
SIDE_BAR_HEIGHT = 450

TOP_BAR_Y = 567
TOP_HUD_LEFT = 70
TOP_HUD_GAP = 120
TOP_CLOCK_RIGHT = 1466
TOP_CLOCK_DATE_Y = 577
TOP_CLOCK_TIME_Y = 555

HOME_BUTTON_WIDTH = 60
HOME_BUTTON_HEIGHT = 60
HOME_BUTTON_LEFT = 40
HOME_BUTTON_TOP = 448
HOME_BUTTON_GAP = 30

STATUS_LABEL_FONT_SIZE = 9
STATUS_VALUE_FONT_SIZE = 15
BUTTON_LABEL_FONT_SIZE = 12
WINDOW_TITLE_FONT_SIZE = 18
WINDOW_CLOSE_FONT_SIZE = 18
WINDOW_MARGIN = 19
WINDOW_HEADER_HEIGHT = 50
WINDOW_HEADER_TOP_PADDING = 6
WINDOW_TITLE_LEFT_PADDING = 18
WINDOW_CLOSE_HALF_SIZE = 13
WINDOW_CLOSE_OFFSET_X = 24
WINDOW_CLOSE_OFFSET_Y = 21
WINDOW_CLOSE_TEXT_OFFSET_Y = 1
SETTINGS_SLIDER_LEFT_PADDING = 36
SETTINGS_SLIDER_RIGHT_PADDING = 36
SETTINGS_SLIDER_TOP_PADDING = 115
SETTINGS_SLIDER_BAR_HEIGHT = 10
SETTINGS_SLIDER_KNOB_RADIUS = 13
SETTINGS_SLIDER_LABEL_SIZE = 18
SETTINGS_SLIDER_VALUE_SIZE = 16
ACTIVITY_MENU_BACK_BUTTON_WIDTH = 150
ACTIVITY_MENU_BACK_BUTTON_HEIGHT = 52
ACTIVITY_MENU_BACK_BUTTON_MARGIN = 24
THRIFTING_BUTTON_IMAGE_PATH = ASSETS_DIR / "thrifting.png"
THRIFTING_BACKGROUND_IMAGE_PATH = ASSETS_DIR / "thrifting.png"
THRIFTING_ART_ASPECT_RATIO = 1500.0 / 900.0
THRIFTING_CLOTHING_IMAGE_PATHS = [
    ASSETS_DIR / "thriftingclothing.png",
    ASSETS_DIR / "thriftingclothing2.png",
    ASSETS_DIR / "thriftingclothing3.png",
    ASSETS_DIR / "thriftingclothing4.png",
    ASSETS_DIR / "thriftingclothing5.png",
]
THRIFTING_RACK_SIZE = 12
THRIFTING_STARTING_MONEY = 100
THRIFTING_XP_PER_LEVEL = 200
THRIFTING_LEVEL_UP_REWARD = 100
FAST_FASHION_FABRICS = ["polyester", "nylon", "rayon", "acrylic"]
ECO_FABRICS = ["cotton", "linen", "wool", "hemp"]
UI_FONT_PATH = ":resources:/fonts/ttf/Kenney/Kenney_Future_Narrow.ttf"
UI_FONT_NAME = "Kenney Future Narrow"

arcade.load_font(UI_FONT_PATH)

THEME_DEEP_PURPLE = (170, 96, 200)
THEME_LAVENDER = (214, 154, 222)
THEME_SOFT_LILAC = (234, 189, 230)
THEME_PALE_PINK = (255, 221, 239)
THEME_TEXT_PURPLE = (106, 47, 130)
THEME_OVERLAY_ALPHA = 70
THRIFTING_WINDOW_FILL = THEME_PALE_PINK
THRIFTING_WINDOW_HEADER = THEME_LAVENDER
THRIFTING_WINDOW_BORDER = THEME_DEEP_PURPLE
THRIFTING_CONTENT_FILL = (255, 247, 251)
THRIFTING_CONTENT_BORDER = THEME_SOFT_LILAC
THRIFTING_TRACK_COLOR = THEME_LAVENDER
THRIFTING_TITLE_COLOR = THEME_TEXT_PURPLE
THRIFTING_WARNING_COLOR = THEME_TEXT_PURPLE
THRIFTING_SUCCESS_COLOR = THEME_DEEP_PURPLE

SOCIAL_MEDIA_WINDOW_FILL = THEME_PALE_PINK
SOCIAL_MEDIA_WINDOW_HEADER = THEME_LAVENDER
SOCIAL_MEDIA_WINDOW_BORDER = THEME_DEEP_PURPLE
SOCIAL_MEDIA_CONTENT_FILL = (255, 248, 252)
SOCIAL_MEDIA_SIDEBAR_FILL = (255, 252, 255)
SOCIAL_MEDIA_SIDEBAR_STRIPE_A = (255, 246, 251)
SOCIAL_MEDIA_SIDEBAR_STRIPE_B = (255, 238, 247)
SOCIAL_MEDIA_CARD_FILL = (255, 255, 255)
SOCIAL_MEDIA_CARD_BORDER = THEME_SOFT_LILAC
SOCIAL_MEDIA_CARD_TEXT = THEME_TEXT_PURPLE
SOCIAL_MEDIA_CARD_MUTED = (172, 129, 169)
SOCIAL_MEDIA_CARD_GOLD = (255, 203, 92)
SOCIAL_MEDIA_CARD_LIFE_TRACK = (251, 221, 235)
SOCIAL_MEDIA_CARD_LIFE_FILL = THEME_LAVENDER
SOCIAL_MEDIA_MODAL_OVERLAY = (255, 226, 239, 180)
SOCIAL_MEDIA_CARD_HEIGHT = 148
SOCIAL_MEDIA_CARD_GAP = 10
SOCIAL_MEDIA_SIDEBAR_MIN_WIDTH = 236
SOCIAL_MEDIA_SIDEBAR_MAX_WIDTH = 292
SOCIAL_MEDIA_COMPOSE_WIDTH = 650
SOCIAL_MEDIA_COMPOSE_HEIGHT = 468
SOCIAL_MEDIA_COOLDOWN_SECONDS = 10 * 60.0
SOCIAL_MEDIA_MAX_NOTIFICATIONS = 5

PRESS_ANIMATION_TIME = 0.18
PRESS_SHRINK_SCALE = 0.86


class BackgroundMusicPlaylist:
    """Play the asset folder's songs back-to-back and loop them forever."""

    def __init__(self, music_dir: Path) -> None:
        self.track_paths = sorted(
            path for path in music_dir.glob("*.mp3") if path.is_file()
        )
        self._sounds: list[pygame.mixer.Sound] = []
        self._channel: Optional[pygame.mixer.Channel] = None
        self._current_sound: Optional[pygame.mixer.Sound] = None
        self._started = False
        self._available = bool(self.track_paths)
        self._volume = 0.7

    def start(self) -> None:
        if self._started or not self._available:
            return

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.set_reserved(1)
            self._sounds = []
            for path in self.track_paths:
                try:
                    self._sounds.append(pygame.mixer.Sound(str(path)))
                except pygame.error:
                    continue
            if not self._sounds:
                raise pygame.error("No playable music tracks were found.")
            self._channel = pygame.mixer.Channel(0)
            self._channel.set_volume(self._volume)
            self._current_sound = self._sounds[0]
            self._channel.play(self._current_sound)
            self._queue_next_track()
            self._started = True
        except pygame.error:
            self._available = False
            self._sounds = []
            self._channel = None
            self._current_sound = None

    def update(self) -> None:
        if not self._started or self._channel is None:
            return

        current_sound = self._channel.get_sound()
        if current_sound is None or current_sound is self._current_sound:
            return

        self._current_sound = current_sound
        self._queue_next_track()

    def set_volume(self, volume: float) -> None:
        self._volume = max(0.0, min(1.0, volume))
        if self._channel is not None:
            self._channel.set_volume(self._volume)

    @property
    def volume(self) -> float:
        return self._volume

    def _queue_next_track(self) -> None:
        if self._channel is None or not self._sounds or self._current_sound is None:
            return

        try:
            current_index = self._sounds.index(self._current_sound)
        except ValueError:
            return

        next_index = (current_index + 1) % len(self._sounds)
        self._channel.queue(self._sounds[next_index])


@dataclass(frozen=True)
class GameLayout:
    """Scaled coordinates and sizes for the current window."""

    width: float
    height: float

    @property
    def scale_x(self) -> float:
        return self.width / BASE_SCREEN_WIDTH

    @property
    def scale_y(self) -> float:
        return self.height / BASE_SCREEN_HEIGHT

    @property
    def ui_scale(self) -> float:
        return min(self.scale_x, self.scale_y)

    def sx(self, value: float) -> float:
        return value * self.scale_x

    def sy(self, value: float) -> float:
        return value * self.scale_y

    def ss(self, value: float) -> float:
        return value * self.ui_scale

    @property
    def side_bar_x(self) -> float:
        return self.sx(SIDE_BAR_X)

    @property
    def side_bar_y(self) -> float:
        return self.sy(SIDE_BAR_Y)

    @property
    def side_bar_width(self) -> float:
        return self.sx(SIDE_BAR_WIDTH)

    @property
    def side_bar_height(self) -> float:
        return self.sy(SIDE_BAR_HEIGHT)

    @property
    def top_bar_y(self) -> float:
        return self.height - self.sy(33)

    @property
    def top_hud_left(self) -> float:
        return self.sx(TOP_HUD_LEFT)

    @property
    def top_hud_gap(self) -> float:
        return self.sx(TOP_HUD_GAP)

    @property
    def top_clock_right(self) -> float:
        return self.width - self.sx(34)

    @property
    def top_clock_date_y(self) -> float:
        return self.top_bar_y + self.sy(10)

    @property
    def top_clock_time_y(self) -> float:
        return self.top_bar_y - self.sy(12)

    @property
    def home_button_width(self) -> float:
        return self.ss(HOME_BUTTON_WIDTH)

    @property
    def home_button_height(self) -> float:
        return self.ss(HOME_BUTTON_HEIGHT)

    @property
    def home_button_left(self) -> float:
        return self.sx(HOME_BUTTON_LEFT)

    @property
    def home_button_top(self) -> float:
        return self.sy(HOME_BUTTON_TOP)

    @property
    def home_button_gap(self) -> float:
        return self.ss(HOME_BUTTON_GAP)

    @property
    def status_label_font_size(self) -> float:
        return self.ss(STATUS_LABEL_FONT_SIZE)

    @property
    def status_value_font_size(self) -> float:
        return self.ss(STATUS_VALUE_FONT_SIZE)

    @property
    def button_label_font_size(self) -> float:
        return self.ss(BUTTON_LABEL_FONT_SIZE)

    @property
    def window_title_font_size(self) -> float:
        return self.ss(WINDOW_TITLE_FONT_SIZE)

    @property
    def window_close_font_size(self) -> float:
        return self.ss(WINDOW_CLOSE_FONT_SIZE)

    @property
    def window_margin(self) -> float:
        return self.ss(WINDOW_MARGIN)

    @property
    def window_header_height(self) -> float:
        return self.sy(WINDOW_HEADER_HEIGHT)

    @property
    def window_header_top_padding(self) -> float:
        return self.sy(WINDOW_HEADER_TOP_PADDING)

    @property
    def window_title_left_padding(self) -> float:
        return self.sx(WINDOW_TITLE_LEFT_PADDING)

    @property
    def window_close_half_size(self) -> float:
        return self.ss(WINDOW_CLOSE_HALF_SIZE)

    @property
    def window_close_offset_x(self) -> float:
        return self.sx(WINDOW_CLOSE_OFFSET_X)

    @property
    def window_close_offset_y(self) -> float:
        return self.sy(WINDOW_CLOSE_OFFSET_Y)

    @property
    def window_close_text_offset_y(self) -> float:
        return self.sy(WINDOW_CLOSE_TEXT_OFFSET_Y)


def _current_time() -> float:
    """Return a monotonic timestamp for animation timing."""
    return time.perf_counter()


def _path_exists(path: Path) -> bool:
    return path.is_file()


def _make_sprite(
    image_path: Path,
    center_x: float,
    center_y: float,
    width: float,
    height: float,
    fallback_color: arcade.Color,
    crop_to_fit: bool = False,
) -> arcade.Sprite:
    """Load a sprite from disk when available, otherwise use a solid block."""
    if _path_exists(image_path):
        if crop_to_fit:
            texture = arcade.load_texture(str(image_path))
            target_aspect = width / height if height else 1.0
            source_aspect = texture.width / texture.height if texture.height else target_aspect
            if source_aspect > target_aspect:
                crop_width = max(1, int(round(texture.height * target_aspect)))
                crop_height = texture.height
                crop_x = max(0, (texture.width - crop_width) // 2)
                crop_y = 0
            else:
                crop_width = texture.width
                crop_height = max(1, int(round(texture.width / target_aspect)))
                crop_x = 0
                crop_y = max(0, (texture.height - crop_height) // 2)
            sprite = arcade.Sprite(texture.crop(crop_x, crop_y, crop_width, crop_height))
        else:
            sprite = arcade.Sprite(str(image_path))
        sprite.center_x = center_x
        sprite.center_y = center_y
        sprite.width = width
        sprite.height = height
        return sprite

    sprite = arcade.SpriteSolidColor(int(width), int(height), fallback_color)
    sprite.center_x = center_x
    sprite.center_y = center_y
    return sprite


def _make_panel(
    center_x: float,
    center_y: float,
    width: float,
    height: float,
    fill_color: arcade.Color,
    alpha: int,
) -> arcade.Sprite:
    sprite = arcade.SpriteSolidColor(int(width), int(height), fill_color)
    sprite.center_x = center_x
    sprite.center_y = center_y
    sprite.alpha = alpha
    return sprite


def _lerp_color(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    t = max(0.0, min(1.0, t))
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _draw_pill(
    x: float,
    y: float,
    width: float,
    height: float,
    fill: tuple[int, int, int],
    border: tuple[int, int, int],
) -> None:
    radius = height / 2
    if width <= height:
        arcade.draw_circle_filled(x + width / 2, y + radius, radius, fill)
        arcade.draw_circle_outline(x + width / 2, y + radius, radius, border, 1)
        return

    arcade.draw_lrbt_rectangle_filled(x + radius, x + width - radius, y, y + height, fill)
    arcade.draw_circle_filled(x + radius, y + radius, radius, fill)
    arcade.draw_circle_filled(x + width - radius, y + radius, radius, fill)
    arcade.draw_circle_outline(x + radius, y + radius, radius, border, 1)
    arcade.draw_circle_outline(x + width - radius, y + radius, radius, border, 1)
    arcade.draw_line(x + radius, y, x + width - radius, y, border, 1)
    arcade.draw_line(x + radius, y + height, x + width - radius, y + height, border, 1)


def _format_compact_count(value: int) -> str:
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"{value / 1_000:.1f}K"
    return str(value)


class DrawableSprite:
    """Small wrapper that renders a single sprite through a SpriteList."""

    def __init__(self, sprite: arcade.Sprite) -> None:
        self._sprite = sprite
        self._sprite_list = arcade.SpriteList()
        self._sprite_list.append(sprite)

    def draw(self) -> None:
        self._sprite_list.draw()

    def collides_with_point(self, point: tuple[float, float]) -> bool:
        return self._sprite.collides_with_point(point)

    @property
    def sprite(self) -> arcade.Sprite:
        return self._sprite

    @property
    def center_x(self) -> float:
        return self._sprite.center_x

    @center_x.setter
    def center_x(self, value: float) -> None:
        self._sprite.center_x = value

    @property
    def center_y(self) -> float:
        return self._sprite.center_y

    @center_y.setter
    def center_y(self, value: float) -> None:
        self._sprite.center_y = value

    @property
    def width(self) -> float:
        return self._sprite.width

    @width.setter
    def width(self, value: float) -> None:
        self._sprite.width = value

    @property
    def height(self) -> float:
        return self._sprite.height

    @height.setter
    def height(self, value: float) -> None:
        self._sprite.height = value

    @property
    def scale(self) -> float:
        return self._sprite.scale

    @scale.setter
    def scale(self, value: float) -> None:
        self._sprite.scale = value

    @property
    def alpha(self) -> int:
        return self._sprite.alpha

    @alpha.setter
    def alpha(self, value: int) -> None:
        self._sprite.alpha = value

    def replace(self, sprite: arcade.Sprite) -> None:
        self._sprite = sprite
        self._sprite_list.clear()
        self._sprite_list.append(sprite)

@dataclass
class StatusBox:
    """Small HUD block for money, energy, or level."""

    layout: GameLayout
    label: str
    value: str
    center_x: float
    center_y: float
    width: float = 132
    height: float = 42
    fill_color: arcade.Color = THEME_PALE_PINK
    border_color: arcade.Color = THEME_LAVENDER
    accent_color: arcade.Color = THEME_DEEP_PURPLE
    label_size: float = STATUS_LABEL_FONT_SIZE
    value_size: float = STATUS_VALUE_FONT_SIZE

    def __post_init__(self) -> None:
        self._build_visuals()

    def _build_visuals(self) -> None:
        self.shadow = DrawableSprite(
            _make_panel(
                self.center_x + self.layout.ss(3),
                self.center_y - self.layout.ss(3),
                self.width,
                self.height,
                THEME_DEEP_PURPLE,
                110,
            )
        )
        self.border = DrawableSprite(
            _make_panel(
                self.center_x,
                self.center_y,
                self.width + self.layout.ss(4),
                self.height + self.layout.ss(4),
                self.border_color,
                255,
            )
        )
        self.panel = DrawableSprite(_make_panel(self.center_x, self.center_y, self.width, self.height, self.fill_color, 220))
        self.accent = DrawableSprite(
            _make_panel(
                self.center_x - self.width * 0.36,
                self.center_y,
                self.layout.ss(4),
                self.height - self.layout.ss(10),
                self.accent_color,
                255,
            )
        )
        if not hasattr(self, "label_text"):
            self.label_text = arcade.Text(
                self.label.upper(),
                self.center_x - self.width * 0.24,
                self.center_y + self.layout.sy(9),
                THEME_TEXT_PURPLE,
                self.label_size,
                font_name=UI_FONT_NAME,
                anchor_x="left",
                anchor_y="center",
            )
            self.value_text = arcade.Text(
                self.value,
                self.center_x - self.width * 0.24,
                self.center_y - self.layout.sy(8),
                THEME_TEXT_PURPLE,
                self.value_size,
                font_name=UI_FONT_NAME,
                anchor_x="left",
                anchor_y="center",
            )
        else:
            self.label_text.x = self.center_x - self.width * 0.24
            self.label_text.y = self.center_y + self.layout.sy(9)
            self.label_text.font_size = self.label_size
            self.value_text.x = self.center_x - self.width * 0.24
            self.value_text.y = self.center_y - self.layout.sy(8)
            self.value_text.font_size = self.value_size

    def update_layout(
        self,
        layout: GameLayout,
        center_x: float,
        center_y: float,
        width: float,
        height: float,
        label_size: float,
        value_size: float,
    ) -> None:
        self.layout = layout
        self.center_x = center_x
        self.center_y = center_y
        self.width = width
        self.height = height
        self.label_size = label_size
        self.value_size = value_size
        self._build_visuals()

    def set_value(self, value: str) -> None:
        self.value = value
        self.value_text.text = value

    def draw(self) -> None:
        self.shadow.draw()
        self.border.draw()
        self.panel.draw()
        self.accent.draw()
        self.label_text.draw()
        self.value_text.draw()


@dataclass
class PlayerWallet:
    """Shared player money state used by both the home HUD and thrift game."""

    amount: int


@dataclass
class PlayerProgress:
    """Shared player progression state used by the home HUD and thrift game."""

    level: int = 1
    experience: int = 0
    highest_rewarded_level: int = 1

    def add_experience(self, amount: int) -> int:
        """Add or remove experience and return the number of new reward levels."""
        if amount == 0:
            return 0

        self.experience += amount
        while self.experience >= THRIFTING_XP_PER_LEVEL:
            self.experience -= THRIFTING_XP_PER_LEVEL
            self.level += 1

        while self.experience < 0 and self.level > 1:
            self.level -= 1
            self.experience += THRIFTING_XP_PER_LEVEL

        if self.experience < 0:
            self.experience = 0

        new_reward_levels = max(0, self.level - self.highest_rewarded_level)
        if new_reward_levels > 0:
            self.highest_rewarded_level = self.level
        return new_reward_levels


@dataclass
class PlayerEnergy:
    """Shared player energy state used by the home HUD and social media game."""

    current: int
    maximum: int = 10
    cooldown_ends_at: float = 0.0

    def percentage_text(self) -> str:
        if self.maximum <= 0:
            return "0%"
        return f"{int(round((self.current / self.maximum) * 100))}%"


class ThriftInfoBox:
    """A detail card that summarizes the currently selected thrift item."""

    def __init__(
        self,
        layout: GameLayout,
        center_x: float,
        center_y: float,
        width: float,
        height: float,
    ) -> None:
        self.layout = layout
        self.center_x = center_x
        self.center_y = center_y
        self.width = width
        self.height = height
        self.title = "Clothing Info"
        self._build_visuals()
        self.set_item(None)

    def _build_visuals(self) -> None:
        self.shadow = DrawableSprite(
            _make_panel(
                self.center_x + self.layout.ss(3),
                self.center_y - self.layout.ss(3),
                self.width,
                self.height,
                THEME_DEEP_PURPLE,
                110,
            )
        )
        self.border = DrawableSprite(
            _make_panel(
                self.center_x,
                self.center_y,
                self.width + self.layout.ss(4),
                self.height + self.layout.ss(4),
                THRIFTING_WINDOW_BORDER,
                255,
            )
        )
        self.panel = DrawableSprite(
            _make_panel(self.center_x, self.center_y, self.width, self.height, THRIFTING_CONTENT_FILL, 230)
        )
        self.accent = DrawableSprite(
            _make_panel(
                self.center_x - self.width * 0.36,
                self.center_y,
                self.layout.ss(4),
                self.height - self.layout.ss(12),
                THRIFTING_SUCCESS_COLOR,
                255,
            )
        )
        title_x = self.center_x - self.width * 0.34
        title_y = self.center_y + self.height * 0.31
        # Give the detail rows a little more breathing room so the labels and values
        # do not visually crowd each other inside the info card.
        line_gap = max(self.layout.sy(22), self.layout.ss(18))
        label_x = self.center_x - self.width * 0.37
        value_x = self.center_x + self.width * 0.34
        if not hasattr(self, "title_text"):
            self.title_text = arcade.Text(
                self.title,
                title_x,
                title_y,
                THRIFTING_TITLE_COLOR,
                self.layout.ss(15),
                font_name=UI_FONT_NAME,
                anchor_x="left",
                anchor_y="center",
            )
            self.labels = [
                arcade.Text(
                    "",
                    label_x,
                    title_y - line_gap * (index + 1),
                    THRIFTING_TITLE_COLOR,
                    self.layout.ss(11),
                    font_name=UI_FONT_NAME,
                    anchor_x="left",
                    anchor_y="center",
                )
                for index in range(3)
            ]
            self.values = [
                arcade.Text(
                    "",
                    value_x,
                    title_y - line_gap * (index + 1),
                    THRIFTING_TITLE_COLOR,
                    self.layout.ss(11),
                    font_name=UI_FONT_NAME,
                    anchor_x="right",
                    anchor_y="center",
                )
                for index in range(3)
            ]
        else:
            self.title_text.x = title_x
            self.title_text.y = title_y
            self.title_text.font_size = self.layout.ss(15)
            for index, text in enumerate(self.labels):
                text.x = label_x
                text.y = title_y - line_gap * (index + 1)
                text.font_size = self.layout.ss(11)
            for index, text in enumerate(self.values):
                text.x = value_x
                text.y = title_y - line_gap * (index + 1)
                text.font_size = self.layout.ss(11)

    def set_item(self, item: Optional["ThriftItem"]) -> None:
        if item is None:
            entries = [
                ("Fabric", "-", THRIFTING_TITLE_COLOR),
                ("Type", "-", THRIFTING_TITLE_COLOR),
                ("Price", "-", THRIFTING_TITLE_COLOR),
            ]
        else:
            entries = [
                ("Fabric", item.fabric.title(), THRIFTING_TITLE_COLOR),
                (
                    "Type",
                    "Eco Friendly" if item.eco else "Fast Fashion",
                    THRIFTING_SUCCESS_COLOR if item.eco else THRIFTING_WARNING_COLOR,
                ),
                ("Price", f"${item.price}", THRIFTING_TITLE_COLOR),
            ]

        for text, (label, value, color) in zip(self.labels, entries):
            text.text = f"{label}:"
            text.color = color
        for text, (_, value, color) in zip(self.values, entries):
            text.text = value
            text.color = color

    def update_layout(
        self,
        layout: GameLayout,
        center_x: float,
        center_y: float,
        width: float,
        height: float,
    ) -> None:
        self.layout = layout
        self.center_x = center_x
        self.center_y = center_y
        self.width = width
        self.height = height
        self._build_visuals()

    def draw(self) -> None:
        self.shadow.draw()
        self.border.draw()
        self.panel.draw()
        self.accent.draw()
        self.title_text.draw()
        for text in self.labels:
            text.draw()
        for text in self.values:
            text.draw()


class HomeButton:
    """A left-side navigation button with a press animation and two visual states."""

    def __init__(
        self,
        layout: GameLayout,
        label: str,
        center_x: float,
        center_y: float,
        on_activate: Callable[[], None],
        active: bool = False,
    ) -> None:
        self.layout = layout
        self.label = label
        self.center_x = center_x
        self.center_y = center_y
        self.on_activate = on_activate
        self.press_started_at: Optional[float] = None
        self.pending_activation = False
        self.is_pressed = False
        self.current_scale = 1.0
        self.is_active = active
        self.normal_sprite = DrawableSprite(self._build_sprite(active=False))
        self.active_sprite = DrawableSprite(self._build_sprite(active=True))
        self.sprite = self.active_sprite if active else self.normal_sprite
        self.show_label = not _path_exists(BUTTON_IMAGE_PATHS[self.label])
        self.text = arcade.Text(
            label.title(),
            center_x,
            center_y,
            THEME_TEXT_PURPLE,
            self.layout.button_label_font_size,
            font_name=UI_FONT_NAME,
            anchor_x="center",
            anchor_y="center",
        )
        self.update_layout(layout, center_x, center_y)

    def _bounds(self) -> tuple[float, float, float, float]:
        half_width = self.layout.home_button_width * self.current_scale / 2
        half_height = self.layout.home_button_height * self.current_scale / 2
        return (
            self.center_x - half_width,
            self.center_x + half_width,
            self.center_y - half_height,
            self.center_y + half_height,
        )

    def _build_sprite(self, active: bool) -> arcade.Sprite:
        image_path = BUTTON_ACTIVE_IMAGE_PATHS.get(self.label) if active else BUTTON_IMAGE_PATHS[self.label]
        fallback_color = THEME_LAVENDER if active else THEME_DEEP_PURPLE
        sprite = _make_sprite(
            image_path if image_path is not None else BUTTON_IMAGE_PATHS[self.label],
            self.center_x,
            self.center_y,
            self.layout.home_button_width,
            self.layout.home_button_height,
            fallback_color,
        )
        sprite.alpha = 230
        return sprite

    def update_layout(self, layout: GameLayout, center_x: float, center_y: float) -> None:
        self.layout = layout
        self.center_x = center_x
        self.center_y = center_y
        for sprite in (self.normal_sprite, self.active_sprite):
            sprite.center_x = center_x
            sprite.center_y = center_y
            sprite.width = layout.home_button_width
            sprite.height = layout.home_button_height
            sprite.scale = self.current_scale
        self.sprite = self.active_sprite if self.is_active else self.normal_sprite
        self.text.x = center_x
        self.text.y = center_y
        self.text.font_size = max(11, int(layout.button_label_font_size * self.current_scale))

    def set_active(self, is_active: bool) -> None:
        self.is_active = is_active
        self.sprite = self.active_sprite if is_active else self.normal_sprite
        for sprite in (self.normal_sprite, self.active_sprite):
            sprite.center_x = self.center_x
            sprite.center_y = self.center_y
            sprite.scale = self.current_scale

    def hit_test(self, x: float, y: float) -> bool:
        left, right, bottom, top = self._bounds()
        return left <= x <= right and bottom <= y <= top

    def press(self, now: float) -> None:
        self.press_started_at = now
        self.pending_activation = True
        self.is_pressed = True
        self.on_activate()

    def release(self) -> None:
        self.pending_activation = False
        self.is_pressed = False

    def update(self, dt: float, now: float) -> None:
        if self.press_started_at is None:
            self.current_scale += (1.0 - self.current_scale) * min(1.0, dt * 12)
        else:
            elapsed = now - self.press_started_at
            if elapsed < PRESS_ANIMATION_TIME / 2:
                self.current_scale = 1.0 - (1.0 - PRESS_SHRINK_SCALE) * (elapsed / (PRESS_ANIMATION_TIME / 2))
            elif elapsed < PRESS_ANIMATION_TIME:
                self.current_scale = PRESS_SHRINK_SCALE + (1.0 - PRESS_SHRINK_SCALE) * (
                    (elapsed - PRESS_ANIMATION_TIME / 2) / (PRESS_ANIMATION_TIME / 2)
                )
            else:
                self.current_scale = 1.0
                self.press_started_at = None

        for sprite in (self.normal_sprite, self.active_sprite):
            sprite.scale = self.current_scale

    def draw(self) -> None:
        self.sprite.draw()
        if self.show_label:
            self.text.font_size = max(11, int(self.layout.button_label_font_size * self.current_scale))
            self.text.draw()

    def reset(self) -> None:
        self.press_started_at = None
        self.pending_activation = False
        self.is_pressed = False
        self.current_scale = 1.0
        for sprite in (self.normal_sprite, self.active_sprite):
            sprite.scale = 1.0


class SpriteButtonPanel:
    """A sprite-backed rectangular button with centered text."""

    def __init__(
        self,
        layout: GameLayout,
        label: str,
        center_x: float,
        center_y: float,
        width: float,
        height: float,
        fill_color: tuple[int, int, int],
        on_activate: Callable[[], None],
        image_path: Optional[Path] = None,
        crop_image_to_fit: bool = False,
        text_color: tuple[int, int, int] = THEME_TEXT_PURPLE,
        text_size: Optional[float] = None,
    ) -> None:
        self.layout = layout
        self.label = label
        self.center_x = center_x
        self.center_y = center_y
        self.width = width
        self.height = height
        self.fill_color = fill_color
        self.on_activate = on_activate
        self.image_path = image_path
        self.crop_image_to_fit = crop_image_to_fit
        self.is_pressed = False
        self.sprite = DrawableSprite(
            _make_sprite(
                image_path,
                center_x,
                center_y,
                width,
                height,
                fill_color,
                crop_to_fit=crop_image_to_fit,
            )
            if image_path is not None
            else _make_panel(center_x, center_y, width, height, fill_color, 255)
        )
        self.text = arcade.Text(
            label,
            center_x,
            center_y,
            text_color,
            text_size if text_size is not None else self._default_text_size(layout),
            font_name=UI_FONT_NAME,
            anchor_x="center",
            anchor_y="center",
        )

    def _default_text_size(self, layout: GameLayout) -> float:
        return max(layout.ss(28), 20)

    def update_layout(
        self,
        layout: GameLayout,
        center_x: float,
        center_y: float,
        width: float,
        height: float,
        text_size: Optional[float] = None,
    ) -> None:
        self.layout = layout
        self.center_x = center_x
        self.center_y = center_y
        self.width = width
        self.height = height
        if self.image_path is not None:
            self.sprite.replace(
                _make_sprite(
                    self.image_path,
                    center_x,
                    center_y,
                    width,
                    height,
                    self.fill_color,
                    crop_to_fit=self.crop_image_to_fit,
                )
            )
        else:
            self.sprite.sprite.center_x = center_x
            self.sprite.sprite.center_y = center_y
            self.sprite.sprite.width = width
            self.sprite.sprite.height = height
        self.text.x = center_x
        self.text.y = center_y
        self.text.font_size = text_size if text_size is not None else self._default_text_size(layout)

    def hit_test(self, x: float, y: float) -> bool:
        left = self.center_x - self.width / 2
        right = self.center_x + self.width / 2
        bottom = self.center_y - self.height / 2
        top = self.center_y + self.height / 2
        return left <= x <= right and bottom <= y <= top

    def activate(self) -> None:
        self.on_activate()

    def press(self) -> None:
        self.is_pressed = True
        self.activate()

    def release(self) -> None:
        self.is_pressed = False

    def draw(self) -> None:
        self.sprite.draw()
        arcade.draw_lrbt_rectangle_outline(
            self.center_x - self.width / 2,
            self.center_x + self.width / 2,
            self.center_y - self.height / 2,
            self.center_y + self.height / 2,
            THEME_DEEP_PURPLE,
            3,
        )
        self.text.draw()


class HomeView(arcade.View):
    """Main dashboard with button sprites and top status boxes."""

    def __init__(self) -> None:
        super().__init__()
        self.music = BackgroundMusicPlaylist(ASSETS_DIR)
        self.layout = GameLayout(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)
        self.wallet = PlayerWallet(THRIFTING_STARTING_MONEY)
        self.progress = PlayerProgress()
        self.energy = PlayerEnergy(10, 10)
        self.background_color = THEME_DEEP_PURPLE
        self.background_sprite = DrawableSprite(self._build_background_sprite(self.layout))
        self.theme_overlay = DrawableSprite(_make_panel(self.layout.width / 2, self.layout.height / 2, self.layout.width, self.layout.height, THEME_SOFT_LILAC, THEME_OVERLAY_ALPHA))
        self.top_bar = DrawableSprite(_make_panel(self.layout.width / 2, self.layout.top_bar_y, self.layout.width, self.layout.sy(92), THEME_LAVENDER, 120))
        self.side_bar = DrawableSprite(_make_panel(self.layout.side_bar_x, self.layout.side_bar_y, self.layout.side_bar_width, self.layout.side_bar_height, THEME_LAVENDER, 220))
        self.money_box = StatusBox(self.layout, "Money", f"${self.wallet.amount}", self.layout.top_hud_left, self.layout.top_bar_y, width=self.layout.ss(132), height=self.layout.ss(42), label_size=self.layout.status_label_font_size, value_size=self.layout.status_value_font_size)
        self.energy_box = StatusBox(self.layout, "Energy", self.energy.percentage_text(), self.layout.top_hud_left + self.layout.top_hud_gap, self.layout.top_bar_y, width=self.layout.ss(132), height=self.layout.ss(42), label_size=self.layout.status_label_font_size, value_size=self.layout.status_value_font_size)
        self.level_box = StatusBox(self.layout, "Level", f"{self.progress.level} ({self.progress.experience}/{THRIFTING_XP_PER_LEVEL})", self.layout.top_hud_left + self.layout.top_hud_gap * 2, self.layout.top_bar_y, width=self.layout.ss(108), height=self.layout.ss(42), accent_color=THEME_DEEP_PURPLE, label_size=self.layout.status_label_font_size, value_size=self.layout.status_value_font_size)
        self.date_text = arcade.Text(
            "",
            self.layout.top_clock_right,
            self.layout.top_clock_date_y,
            THEME_TEXT_PURPLE,
            self.layout.ss(14),
            font_name=UI_FONT_NAME,
            anchor_x="right",
            anchor_y="center",
        )
        self.time_text = arcade.Text(
            "",
            self.layout.top_clock_right,
            self.layout.top_clock_time_y,
            THEME_TEXT_PURPLE,
            self.layout.ss(18),
            font_name=UI_FONT_NAME,
            anchor_x="right",
            anchor_y="center",
        )
        self.buttons: list[HomeButton] = []
        self.active_window: Optional[ComputerWindowOverlay] = None
        self.social_media_window: Optional[SocialMediaGameOverlay] = None
        self._pressed_button: Optional[HomeButton] = None
        self._build_buttons()
        self._sync_clock_text()
        self._apply_layout(self.layout)

    def _build_background_sprite(self, layout: GameLayout) -> arcade.Sprite:
        return _make_sprite(
            BACKGROUND_IMAGE,
            layout.width / 2,
            layout.height / 2,
            layout.width,
            layout.height,
            THEME_DEEP_PURPLE,
        )

    def _sync_clock_text(self) -> None:
        now = datetime.now()
        self.date_text.text = now.strftime("%b %d, %Y")
        self.time_text.text = now.strftime("%I:%M %p").lstrip("0")

    def _sync_money_box(self) -> None:
        self.money_box.set_value(f"${self.wallet.amount}")

    def _sync_energy_box(self) -> None:
        self.energy_box.set_value(self.energy.percentage_text())

    def _sync_level_box(self) -> None:
        self.level_box.set_value(f"{self.progress.level} ({self.progress.experience}/{THRIFTING_XP_PER_LEVEL})")

    def _build_buttons(self) -> None:
        labels = [
            "settings",
            "social media",
            "closet",
            "clothing store",
            "activity center",
        ]
        for index, label in enumerate(labels):
            center_y = self.layout.home_button_top - index * (self.layout.home_button_height + self.layout.home_button_gap)
            button = HomeButton(
                self.layout,
                label,
                self.layout.home_button_left + self.layout.home_button_width / 2,
                center_y,
                self._make_open_action(label),
            )
            self.buttons.append(button)

    def _apply_layout(self, layout: GameLayout) -> None:
        self.layout = layout
        self.background_sprite.center_x = layout.width / 2
        self.background_sprite.center_y = layout.height / 2
        self.background_sprite.width = layout.width
        self.background_sprite.height = layout.height
        self.theme_overlay.center_x = layout.width / 2
        self.theme_overlay.center_y = layout.height / 2
        self.theme_overlay.width = layout.width
        self.theme_overlay.height = layout.height
        self.top_bar.center_x = layout.width / 2
        self.top_bar.center_y = layout.top_bar_y
        self.top_bar.width = layout.width
        self.top_bar.height = layout.sy(92)
        self.side_bar.center_x = layout.side_bar_x
        self.side_bar.center_y = layout.side_bar_y
        self.side_bar.width = layout.side_bar_width
        self.side_bar.height = layout.side_bar_height
        self.money_box.update_layout(
            layout,
            layout.top_hud_left,
            layout.top_bar_y,
            layout.ss(132),
            layout.ss(42),
            layout.status_label_font_size,
            layout.status_value_font_size,
        )
        self.energy_box.update_layout(
            layout,
            layout.top_hud_left + layout.top_hud_gap,
            layout.top_bar_y,
            layout.ss(132),
            layout.ss(42),
            layout.status_label_font_size,
            layout.status_value_font_size,
        )
        self.level_box.update_layout(
            layout,
            layout.top_hud_left + layout.top_hud_gap * 2,
            layout.top_bar_y,
            layout.ss(108),
            layout.ss(42),
            layout.status_label_font_size,
            layout.status_value_font_size,
        )
        self.date_text.x = layout.top_clock_right
        self.date_text.y = layout.top_clock_date_y
        self.date_text.font_size = layout.ss(14)
        self.time_text.x = layout.top_clock_right
        self.time_text.y = layout.top_clock_time_y
        self.time_text.font_size = layout.ss(18)
        button_left = layout.home_button_left + layout.home_button_width / 2
        for index, button in enumerate(self.buttons):
            center_y = layout.home_button_top - index * (layout.home_button_height + layout.home_button_gap)
            button.update_layout(layout, button_left, center_y)
        if self.active_window is not None:
            self.active_window.update_layout(layout)

    def _make_open_action(self, label: str) -> Callable[[], None]:
        def open_window() -> None:
            if label == "activity center":
                self._open_activity_menu()
                return
            if self.active_window is not None and self.active_window.title == label.title():
                self.active_window.close()
                return
            self._open_window(label)

        return open_window

    def _open_activity_menu(self) -> None:
        self.active_window = ActivityWindowOverlay(
            self.layout,
            self._close_activity_window,
            self._open_thrifting_game,
            self.music,
        )

    def _close_activity_window(self) -> None:
        self.active_window = None

    def _open_thrifting_game(self) -> None:
        self.active_window = ThriftingGameOverlay(
            self.layout,
            self._open_activity_menu,
            self.wallet,
            self.progress,
            self.music,
        )

    def _open_window(self, label: str) -> None:
        if self.active_window is not None and self.active_window.title == "Social Media" and label != "social media":
            self._set_button_active("social media", False)
        if label == "social media":
            self._set_button_active(label, True)
            if self.social_media_window is None:
                self.social_media_window = SocialMediaGameOverlay(
                    self.layout,
                    lambda: self._close_window(label),
                    self.energy,
                    self.music,
                )
            else:
                self.social_media_window.update_layout(self.layout)
            self.active_window = self.social_media_window
            return
        self.active_window = ComputerWindowOverlay(
            self.layout,
            title=label.title(),
            on_close=lambda: self._close_window(label),
            music=self.music,
        )

    def _set_button_active(self, label: str, is_active: bool) -> None:
        for button in self.buttons:
            if button.label == label:
                button.set_active(is_active)
                break

    def _close_window(self, label: str) -> None:
        self.active_window = None
        if label == "social media":
            self._set_button_active(label, False)

    def on_show_view(self) -> None:
        arcade.set_background_color(self.background_color)
        self.music.start()
        self._pressed_button = None
        for button in self.buttons:
            button.reset()
        if self.window is not None:
            self._apply_layout(GameLayout(self.window.width, self.window.height))
        if self.social_media_window is not None:
            self.social_media_window.update_layout(self.layout)
        self._sync_money_box()
        self._sync_energy_box()
        self._sync_level_box()

    def on_draw(self) -> None:
        self.clear()
        self.background_sprite.draw()
        self.theme_overlay.draw()
        self.top_bar.draw()
        self.side_bar.draw()
        self.money_box.draw()
        self.energy_box.draw()
        self.level_box.draw()
        self.date_text.draw()
        self.time_text.draw()
        for button in self.buttons:
            button.draw()
        if self.active_window is not None:
            self.active_window.draw()

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int) -> None:
        if button != arcade.MOUSE_BUTTON_LEFT:
            return

        now = _current_time()
        for nav_button in self.buttons:
            if nav_button.hit_test(x, y):
                nav_button.press(now)
                self._pressed_button = nav_button
                return

        if self.active_window is not None and self.active_window.on_mouse_press(x, y, button, modifiers):
            return

    def on_update(self, delta_time: float) -> None:
        now = _current_time()
        self.music.update()
        if self.active_window is not None:
            self.active_window.on_update(delta_time)
        if self.social_media_window is not None and self.social_media_window is not self.active_window:
            self.social_media_window.on_update(delta_time)
        self._sync_clock_text()
        self._sync_money_box()
        self._sync_energy_box()
        self._sync_level_box()
        for nav_button in self.buttons:
            nav_button.update(delta_time, now)

    def on_mouse_drag(
        self,
        x: float,
        y: float,
        dx: float,
        dy: float,
        buttons: int,
        modifiers: int,
    ) -> None:
        if self.active_window is not None:
            self.active_window.on_mouse_drag(x, y, dx, dy, buttons, modifiers)

    def on_mouse_scroll(self, x: float, y: float, scroll_x: float, scroll_y: float) -> None:
        if self.active_window is not None:
            self.active_window.on_mouse_scroll(x, y, scroll_x, scroll_y)

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float) -> None:
        if self.active_window is not None:
            self.active_window.on_mouse_motion(x, y, dx, dy)

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int) -> None:
        if button != arcade.MOUSE_BUTTON_LEFT:
            return

        if self._pressed_button is not None:
            pressed_button = self._pressed_button
            self._pressed_button = None
            pressed_button.release()
            return

        if self.active_window is not None:
            self.active_window.on_mouse_release(x, y, button, modifiers)

    def on_key_press(self, key: int, modifiers: int) -> None:
        if self.active_window is not None:
            self.active_window.on_key_press(key, modifiers)
            return
        if key == arcade.key.ESCAPE:
            return

    def on_resize(self, width: float, height: float) -> None:
        self._apply_layout(GameLayout(width, height))


class ActivityMenuView(arcade.View):
    """Full-screen activity choices for the activity center."""

    def __init__(self, home_view: HomeView, music: BackgroundMusicPlaylist) -> None:
        super().__init__()
        self.home_view = home_view
        self.music = music
        self.layout = GameLayout(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)
        self.background_color = THEME_PALE_PINK
        self.left_button: Optional[SpriteButtonPanel] = None
        self.right_button: Optional[SpriteButtonPanel] = None
        self.home_button: Optional[SpriteButtonPanel] = None
        self._apply_layout(self.layout)

    def _show_home(self) -> None:
        if self.window is not None:
            self.window.show_view(self.home_view)

    def _open_upcycling(self) -> None:
        if self.window is not None:
            self.window.show_view(UpcyclingStationView(self.home_view, self, self.music))

    def _open_thrifting(self) -> None:
        if self.window is not None:
            self.window.show_view(ThriftingView(self.home_view, self, self.music))

    def _apply_layout(self, layout: GameLayout) -> None:
        self.layout = layout
        half_width = layout.width / 2
        full_height = layout.height
        left_center_x = half_width / 2
        right_center_x = half_width + half_width / 2
        button_height = full_height
        button_width = half_width
        if self.left_button is None:
            self.left_button = SpriteButtonPanel(
                layout,
                "Upcycling Station",
                left_center_x,
                full_height / 2,
                button_width,
                button_height,
                THRIFTING_WINDOW_FILL,
                self._open_upcycling,
                text_size=layout.ss(34),
            )
        else:
            self.left_button.update_layout(layout, left_center_x, full_height / 2, button_width, button_height, layout.ss(34))
        if self.right_button is None:
            self.right_button = SpriteButtonPanel(
                layout,
                "Thrifting",
                right_center_x,
                full_height / 2,
                button_width,
                button_height,
                THRIFTING_CONTENT_FILL,
                self._open_thrifting,
                image_path=THRIFTING_BUTTON_IMAGE_PATH,
                text_size=layout.ss(38),
            )
        else:
            self.right_button.update_layout(layout, right_center_x, full_height / 2, button_width, button_height, layout.ss(38))
        if self.home_button is None:
            self.home_button = SpriteButtonPanel(
                layout,
                "Home",
                layout.sx(76),
                layout.height - layout.sy(48),
                layout.ss(ACTIVITY_MENU_BACK_BUTTON_WIDTH),
                layout.ss(ACTIVITY_MENU_BACK_BUTTON_HEIGHT),
                (255, 243, 248),
                self._show_home,
                text_size=layout.ss(22),
            )
        else:
            self.home_button.update_layout(
                layout,
                layout.sx(76),
                layout.height - layout.sy(48),
                layout.ss(ACTIVITY_MENU_BACK_BUTTON_WIDTH),
                layout.ss(ACTIVITY_MENU_BACK_BUTTON_HEIGHT),
                layout.ss(22),
            )

    def on_show_view(self) -> None:
        arcade.set_background_color(self.background_color)
        self.music.start()
        if self.window is not None:
            self._apply_layout(GameLayout(self.window.width, self.window.height))

    def on_draw(self) -> None:
        self.clear()
        if self.left_button is not None:
            self.left_button.draw()
        if self.right_button is not None:
            self.right_button.draw()
        if self.home_button is not None:
            self.home_button.draw()

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int) -> bool:
        if button != arcade.MOUSE_BUTTON_LEFT:
            return False
        if self.left_button is not None and self.left_button.hit_test(x, y):
            self.left_button.press()
            return True
        if self.right_button is not None and self.right_button.hit_test(x, y):
            self.right_button.press()
            return True
        if self.home_button is not None and self.home_button.hit_test(x, y):
            self.home_button.press()
            return True
        return False

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int) -> None:
        if button != arcade.MOUSE_BUTTON_LEFT:
            return
        if self.left_button is not None:
            self.left_button.release()
        if self.right_button is not None:
            self.right_button.release()
        if self.home_button is not None:
            self.home_button.release()

    def on_key_press(self, key: int, modifiers: int) -> None:
        if key == arcade.key.ESCAPE:
            self._show_home()

    def on_resize(self, width: float, height: float) -> None:
        self._apply_layout(GameLayout(width, height))


class ActivityDetailView(arcade.View):
    """Simple destination screen reached from the activity menu."""

    def __init__(
        self,
        home_view: HomeView,
        activity_menu_view: ActivityMenuView,
        music: BackgroundMusicPlaylist,
        title: str,
        description: str,
        background_color: tuple[int, int, int],
        accent_color: tuple[int, int, int],
    ) -> None:
        super().__init__()
        self.home_view = home_view
        self.activity_menu_view = activity_menu_view
        self.music = music
        self.title = title
        self.description = description
        self.background_color = background_color
        self.accent_color = accent_color
        self.layout = GameLayout(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)
        self.title_text = arcade.Text(
            self.title,
            0,
            0,
            THEME_TEXT_PURPLE,
            self.layout.ss(42),
            font_name=UI_FONT_NAME,
            anchor_x="center",
            anchor_y="center",
        )
        self.description_text = arcade.Text(
            self.description,
            0,
            0,
            THEME_TEXT_PURPLE,
            self.layout.ss(22),
            font_name=UI_FONT_NAME,
            anchor_x="center",
            anchor_y="center",
        )
        self.back_button: Optional[SpriteButtonPanel] = None
        self.home_button: Optional[SpriteButtonPanel] = None
        self._apply_layout(self.layout)

    def _go_back(self) -> None:
        if self.window is not None:
            self.window.show_view(self.activity_menu_view)

    def _go_home(self) -> None:
        if self.window is not None:
            self.window.show_view(self.home_view)

    def _apply_layout(self, layout: GameLayout) -> None:
        self.layout = layout
        self.title_text.x = layout.width / 2
        self.title_text.y = layout.height - layout.sy(88)
        self.title_text.font_size = layout.ss(42)
        self.description_text.x = layout.width / 2
        self.description_text.y = layout.height / 2
        self.description_text.font_size = layout.ss(22)
        if self.back_button is None:
            self.back_button = SpriteButtonPanel(
                layout,
                "Back",
                layout.sx(74),
                layout.height - layout.sy(48),
                layout.ss(ACTIVITY_MENU_BACK_BUTTON_WIDTH),
                layout.ss(ACTIVITY_MENU_BACK_BUTTON_HEIGHT),
                self.accent_color,
                self._go_back,
                text_size=layout.ss(22),
            )
        else:
            self.back_button.update_layout(
                layout,
                layout.sx(74),
                layout.height - layout.sy(48),
                layout.ss(ACTIVITY_MENU_BACK_BUTTON_WIDTH),
                layout.ss(ACTIVITY_MENU_BACK_BUTTON_HEIGHT),
                layout.ss(22),
            )
        if self.home_button is None:
            self.home_button = SpriteButtonPanel(
                layout,
                "Home",
                layout.sx(196),
                layout.height - layout.sy(48),
                layout.ss(ACTIVITY_MENU_BACK_BUTTON_WIDTH),
                layout.ss(ACTIVITY_MENU_BACK_BUTTON_HEIGHT),
                (255, 243, 248),
                self._go_home,
                text_size=layout.ss(22),
            )
        else:
            self.home_button.update_layout(
                layout,
                layout.sx(196),
                layout.height - layout.sy(48),
                layout.ss(ACTIVITY_MENU_BACK_BUTTON_WIDTH),
                layout.ss(ACTIVITY_MENU_BACK_BUTTON_HEIGHT),
                layout.ss(22),
            )

    def on_show_view(self) -> None:
        arcade.set_background_color(self.background_color)
        self.music.start()
        if self.window is not None:
            self._apply_layout(GameLayout(self.window.width, self.window.height))

    def on_draw(self) -> None:
        self.clear()
        arcade.draw_lrbt_rectangle_filled(
            0,
            self.layout.width,
            0,
            self.layout.height,
            self.background_color,
        )
        arcade.draw_circle_filled(
            self.layout.width / 2,
            self.layout.height / 2,
            self.layout.ss(120),
            self.accent_color,
        )
        self.title_text.draw()
        self.description_text.draw()
        if self.back_button is not None:
            self.back_button.draw()
        if self.home_button is not None:
            self.home_button.draw()

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int) -> bool:
        if button != arcade.MOUSE_BUTTON_LEFT:
            return False
        if self.back_button is not None and self.back_button.hit_test(x, y):
            self.back_button.press()
            return True
        if self.home_button is not None and self.home_button.hit_test(x, y):
            self.home_button.press()
            return True
        return False

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int) -> None:
        if button != arcade.MOUSE_BUTTON_LEFT:
            return
        if self.back_button is not None:
            self.back_button.release()
        if self.home_button is not None:
            self.home_button.release()

    def on_key_press(self, key: int, modifiers: int) -> None:
        if key == arcade.key.ESCAPE:
            self._go_back()

    def on_resize(self, width: float, height: float) -> None:
        self._apply_layout(GameLayout(width, height))


class UpcyclingStationView(ActivityDetailView):
    def __init__(self, home_view: HomeView, activity_menu_view: ActivityMenuView, music: BackgroundMusicPlaylist) -> None:
        super().__init__(
            home_view,
            activity_menu_view,
            music,
            "Upcycling Station",
            "Turn old pieces into something fresh.",
            THRIFTING_CONTENT_FILL,
            THRIFTING_WINDOW_FILL,
        )


class ThriftingView(ActivityDetailView):
    def __init__(self, home_view: HomeView, activity_menu_view: ActivityMenuView, music: BackgroundMusicPlaylist) -> None:
        super().__init__(
            home_view,
            activity_menu_view,
            music,
            "Thrifting",
            "Browse and build the perfect thrift look.",
            THRIFTING_CONTENT_FILL,
            THRIFTING_WINDOW_HEADER,
        )


class ComputerWindowOverlay:
    """A draggable computer-style window drawn on top of the home screen."""

    def __init__(
        self,
        layout: GameLayout,
        title: str,
        on_close: Callable[[], None],
        music: Optional[BackgroundMusicPlaylist] = None,
    ) -> None:
        self.layout = layout
        self.title = title
        self.on_close = on_close
        self.music = music
        self.window_width = 0.0
        self.window_height = 0.0
        self.window_x = 0.0
        self.window_y = 0.0
        self.is_dragging = False
        self.drag_offset_x = 0.0
        self.drag_offset_y = 0.0
        self.is_adjusting_volume = False
        self.title_text = arcade.Text(
            self.title,
            0,
            0,
            THEME_TEXT_PURPLE,
            layout.window_title_font_size,
            font_name=UI_FONT_NAME,
            anchor_x="left",
            anchor_y="center",
        )
        self.close_text = arcade.Text(
            "x",
            0,
            0,
            THEME_TEXT_PURPLE,
            layout.window_close_font_size,
            font_name=UI_FONT_NAME,
            anchor_x="center",
            anchor_y="center",
        )
        self.settings_label_text = arcade.Text(
            "Music Volume",
            0,
            0,
            THEME_TEXT_PURPLE,
            layout.ss(SETTINGS_SLIDER_LABEL_SIZE),
            font_name=UI_FONT_NAME,
            anchor_x="left",
            anchor_y="center",
        )
        self.settings_value_text = arcade.Text(
            "",
            0,
            0,
            THEME_TEXT_PURPLE,
            layout.ss(SETTINGS_SLIDER_VALUE_SIZE),
            font_name=UI_FONT_NAME,
            anchor_x="right",
            anchor_y="center",
        )
        self.update_layout(layout)

    def _bounds(self) -> tuple[float, float, float, float]:
        left = self.window_x - self.window_width / 2
        right = self.window_x + self.window_width / 2
        bottom = self.window_y - self.window_height / 2
        top = self.window_y + self.window_height / 2
        return left, right, bottom, top

    def _header_bounds(self) -> tuple[float, float, float, float]:
        left, right, _, top = self._bounds()
        return left, right, top - self.layout.window_header_height, top - self.layout.window_header_top_padding

    def _close_bounds(self) -> tuple[float, float, float, float]:
        _, right, _, top = self._bounds()
        center_x = right - self.layout.window_close_offset_x
        center_y = top - self.layout.window_close_offset_y
        return (
            center_x - self.layout.window_close_half_size,
            center_x + self.layout.window_close_half_size,
            center_y - self.layout.window_close_half_size,
            center_y + self.layout.window_close_half_size,
        )

    def _sync_text_positions(self) -> None:
        left, right, _, top = self._bounds()
        _, _, header_bottom, header_top = self._header_bounds()
        close_left, close_right, close_bottom, close_top = self._close_bounds()
        self.title_text.x = left + self.layout.window_title_left_padding
        self.title_text.y = (header_bottom + header_top) / 2
        self.close_text.x = (close_left + close_right) / 2
        self.close_text.y = (close_bottom + close_top) / 2 - self.layout.window_close_text_offset_y
        if self.title == "Settings":
            slider_left, slider_right, slider_center_y = self._slider_geometry()
            self.settings_label_text.x = slider_left
            self.settings_label_text.y = slider_center_y + self.layout.sy(30)
            self.settings_value_text.x = slider_right
            self.settings_value_text.y = slider_center_y + self.layout.sy(30)
            if self.music is not None:
                self.settings_value_text.text = f"{int(round(self.music.volume * 100))}%"

    def _slider_geometry(self) -> tuple[float, float, float]:
        left, right, _, top = self._bounds()
        slider_left = left + self.layout.sx(SETTINGS_SLIDER_LEFT_PADDING)
        slider_right = right - self.layout.sx(SETTINGS_SLIDER_RIGHT_PADDING)
        slider_center_y = top - self.layout.sy(SETTINGS_SLIDER_TOP_PADDING)
        return slider_left, slider_right, slider_center_y

    def _slider_bounds(self) -> tuple[float, float, float, float]:
        slider_left, slider_right, slider_center_y = self._slider_geometry()
        half_height = self.layout.sy(SETTINGS_SLIDER_BAR_HEIGHT) / 2
        return slider_left, slider_right, slider_center_y - half_height, slider_center_y + half_height

    def _slider_knob_center_x(self) -> float:
        slider_left, slider_right, _ = self._slider_geometry()
        if self.music is None:
            return slider_left
        return slider_left + (slider_right - slider_left) * self.music.volume

    def _set_music_volume_from_x(self, x: float) -> None:
        if self.music is None:
            return
        slider_left, slider_right, _ = self._slider_geometry()
        if slider_right <= slider_left:
            return
        volume = (x - slider_left) / (slider_right - slider_left)
        self.music.set_volume(volume)
        self.settings_value_text.text = f"{int(round(self.music.volume * 100))}%"

    def update_layout(self, layout: GameLayout) -> None:
        self.layout = layout
        self.window_width = max(layout.ss(240), min(layout.sx(560), layout.width - layout.window_margin * 2))
        self.window_height = max(layout.ss(180), min(layout.sy(390), layout.height - layout.window_margin * 2))
        self._set_center(layout.width / 2, layout.height / 2 - layout.sy(8))
        self.title_text.font_size = layout.window_title_font_size
        self.close_text.font_size = layout.window_close_font_size
        self.settings_label_text.font_size = layout.ss(SETTINGS_SLIDER_LABEL_SIZE)
        self.settings_value_text.font_size = layout.ss(SETTINGS_SLIDER_VALUE_SIZE)

    def _clamp_position(self, center_x: float, center_y: float) -> tuple[float, float]:
        half_width = self.window_width / 2
        half_height = self.window_height / 2
        min_x = half_width + self.layout.window_margin
        max_x = self.layout.width - half_width - self.layout.window_margin
        min_y = half_height + self.layout.window_margin
        max_y = self.layout.height - half_height - self.layout.window_margin
        return (
            max(min_x, min(center_x, max_x)),
            max(min_y, min(center_y, max_y)),
        )

    def _set_center(self, center_x: float, center_y: float) -> None:
        self.window_x, self.window_y = self._clamp_position(center_x, center_y)
        self._sync_text_positions()

    def _close(self) -> None:
        self.on_close()

    def on_draw(self) -> None:
        left, right, bottom, top = self._bounds()
        header_left, header_right, header_bottom, header_top = self._header_bounds()
        close_left, close_right, close_bottom, close_top = self._close_bounds()
        shadow_offset = self.layout.ss(5)
        arcade.draw_lrbt_rectangle_filled(
            left + shadow_offset,
            right + shadow_offset,
            bottom - shadow_offset,
            top - shadow_offset,
            THEME_DEEP_PURPLE,
        )
        arcade.draw_lrbt_rectangle_filled(
            left,
            right,
            bottom,
            top,
            THEME_PALE_PINK,
        )
        arcade.draw_lrbt_rectangle_outline(
            left,
            right,
            bottom,
            top,
            THEME_DEEP_PURPLE,
            3,
        )
        arcade.draw_lrbt_rectangle_filled(
            header_left,
            header_right,
            header_bottom,
            header_top,
            THEME_LAVENDER,
        )
        self.title_text.draw()
        arcade.draw_lrbt_rectangle_filled(
            close_left,
            close_right,
            close_bottom,
            close_top,
            THEME_SOFT_LILAC,
        )
        self.close_text.draw()
        if self.title == "Settings":
            slider_left, slider_right, slider_bottom, slider_top = self._slider_bounds()
            knob_x = self._slider_knob_center_x()
            knob_y = (slider_bottom + slider_top) / 2
            arcade.draw_lrbt_rectangle_filled(
                slider_left,
                slider_right,
                slider_bottom,
                slider_top,
                THEME_LAVENDER,
            )
            arcade.draw_lrbt_rectangle_outline(
                slider_left,
                slider_right,
                slider_bottom,
                slider_top,
                THEME_DEEP_PURPLE,
                2,
            )
            arcade.draw_circle_filled(
                knob_x,
                knob_y,
                self.layout.ss(SETTINGS_SLIDER_KNOB_RADIUS),
                THEME_DEEP_PURPLE,
            )
            arcade.draw_circle_outline(
                knob_x,
                knob_y,
                self.layout.ss(SETTINGS_SLIDER_KNOB_RADIUS),
                THEME_PALE_PINK,
                2,
            )
            self.settings_label_text.draw()
            self.settings_value_text.draw()

    def draw(self) -> None:
        self.on_draw()

    def on_update(self, delta_time: float) -> None:
        pass

    def _hit_test_slider(self, x: float, y: float) -> bool:
        if self.title != "Settings":
            return False
        left, right, bottom, top = self._slider_bounds()
        if left <= x <= right and bottom <= y <= top:
            return True
        knob_x = self._slider_knob_center_x()
        knob_y = (bottom + top) / 2
        knob_radius = self.layout.ss(SETTINGS_SLIDER_KNOB_RADIUS) * 1.3
        return (x - knob_x) ** 2 + (y - knob_y) ** 2 <= knob_radius**2

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int) -> None:
        if button != arcade.MOUSE_BUTTON_LEFT:
            return False

        close_left, close_right, close_bottom, close_top = self._close_bounds()
        if close_left <= x <= close_right and close_bottom <= y <= close_top:
            self._close()
            return True

        left, right, _, top = self._bounds()
        header_left, header_right, header_bottom, header_top = self._header_bounds()
        bottom = self.window_y - self.window_height / 2
        if left <= x <= right and bottom <= y <= top:
            if header_left <= x <= header_right and header_bottom <= y <= header_top:
                self.is_dragging = True
                self.drag_offset_x = x - self.window_x
                self.drag_offset_y = y - self.window_y
                return True
            if self._hit_test_slider(x, y):
                self.is_adjusting_volume = True
                self._set_music_volume_from_x(x)
                return True
            return True
        return False

    def on_mouse_drag(
        self,
        x: float,
        y: float,
        dx: float,
        dy: float,
        buttons: int,
        modifiers: int,
    ) -> None:
        if self.is_dragging and buttons & arcade.MOUSE_BUTTON_LEFT:
            self._set_center(x - self.drag_offset_x, y - self.drag_offset_y)
        elif self.is_adjusting_volume and buttons & arcade.MOUSE_BUTTON_LEFT:
            self._set_music_volume_from_x(x)

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int) -> None:
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.is_dragging = False
            self.is_adjusting_volume = False

    def on_mouse_scroll(self, x: float, y: float, scroll_x: float, scroll_y: float) -> bool:
        return False

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float) -> None:
        pass

    def on_key_press(self, key: int, modifiers: int) -> None:
        if key == arcade.key.ESCAPE:
            self._close()

    def close(self) -> None:
        self._close()

    def on_resize(self, width: float, height: float) -> None:
        self.update_layout(GameLayout(width, height))


class SocialMediaPostType(Enum):
    OOTD = (
        "OOTD",
        ((218, 198, 250), (188, 168, 222), (255, 255, 255)),
        0.15,
        0.20,
        80,
        "Thrifted outfit check-in with reliable reach.",
        1,
    )
    HAUL = (
        "HAUL",
        ((186, 221, 248), (156, 191, 220), (255, 255, 255)),
        0.18,
        0.25,
        120,
        "Secondhand haul with strong discovery potential.",
        2,
    )
    TUTORIAL = (
        "TUTORIAL",
        ((188, 238, 218), (158, 208, 188), (255, 255, 255)),
        0.10,
        0.18,
        110,
        "Upcycling guide that builds trust over time.",
        4,
    )
    ARTICLE = (
        "ARTICLE",
        ((255, 178, 210), (225, 148, 180), (255, 255, 255)),
        0.06,
        0.12,
        150,
        "Slow fashion think-piece with long shelf life.",
        5,
    )
    REVIEW = (
        "REVIEW",
        ((255, 214, 188), (225, 182, 158), (255, 255, 255)),
        0.20,
        0.15,
        90,
        "Brand review that can spark a quick conversation.",
        2,
    )

    def __init__(
        self,
        label: str,
        bar: tuple[tuple[int, int, int], tuple[int, int, int], tuple[int, int, int]],
        viral_chance: float,
        base_growth: float,
        max_age: float,
        desc: str,
        eco_points: int,
    ) -> None:
        self.label = label
        self.bar = bar
        self.viral_chance = viral_chance
        self.base_growth = base_growth
        self.max_age = max_age
        self.desc = desc
        self.eco_points = eco_points

    @property
    def color(self) -> tuple[int, int, int]:
        return self.bar[0]

    @property
    def border(self) -> tuple[int, int, int]:
        return self.bar[1]

    @property
    def dot_color(self) -> tuple[int, int, int]:
        return self.bar[2]


SOCIAL_MEDIA_TEMPLATES: dict[SocialMediaPostType, list[str]] = {
    SocialMediaPostType.OOTD: [
        "thrifted this whole fit and i am very normal about it ♡",
        "today's outfit is 100% secondhand and i feel unstoppable",
        "tiny closet, big vibe, no fast fashion needed",
        "styled one vintage blazer three ways and now i'm attached",
        "today's look: rescued, reworn, and fully serving",
    ],
    SocialMediaPostType.HAUL: [
        "come thrift with me! everything under budget and full of charm",
        "weekend haul: the best finds were definitely the weirdest ones",
        "secondhand haul recap: a little chaos, a lot of treasure",
        "what i pulled from the charity shop this week ♡",
        "i went looking for one thing and came home with a whole vibe",
    ],
    SocialMediaPostType.TUTORIAL: [
        "how i turned an old shirt into something i actually want to wear",
        "upcycling basics: my favorite no-stress fixes for worn clothes",
        "mending guide for beginners who want their clothes to last",
        "simple diy repair trick that saved my favorite top",
        "a tiny sewing project that made a huge difference",
    ],
    SocialMediaPostType.ARTICLE: [
        "why slow fashion matters more than a trendy launch ever will",
        "the hidden cost of cheap clothing, explained simply",
        "what greenwashing looks like when brands get too polished",
        "a quick breakdown of why textile waste keeps piling up",
        "building a thoughtful wardrobe without falling for hype",
    ],
    SocialMediaPostType.REVIEW: [
        "honest review: is this 'eco' brand actually worth the price?",
        "i tested a sustainable label so you don't have to",
        "reviewing a brand's claims, quality, and transparency",
        "thrift comparison vs. fast fashion: the receipts are here",
        "what i look for before i trust a clothing brand again",
    ],
}

SOCIAL_MEDIA_MILESTONES = [
    (250, "First Followers", "your feed found its first fans ♡"),
    (1_000, "Style Spark", "people are starting to notice ♡"),
    (5_000, "Trend Setter", "your posts are shaping the conversation ♡"),
    (15_000, "Feed Favorite", "the algorithm is on your side ♡"),
    (50_000, "Influence Icon", "your message is impossible to ignore ♡"),
    (100_000, "Fashion Legend", "you changed the feed forever ♡"),
]


@dataclass
class SocialMediaPost:
    ptype: SocialMediaPostType
    text: str
    quality: float
    likes: int = 0
    shares: int = 0
    comments: int = 0
    age: float = 0.0
    is_viral: bool = False
    viral_mult: float = 1.0
    viral_flash: float = 0.0
    dead: bool = False

    @property
    def engagement(self) -> int:
        return self.likes + self.shares * 3 + self.comments * 2

    @property
    def follower_rate(self) -> float:
        return self.engagement * self.quality * self.viral_mult * 0.004

    def tick(self, dt: float) -> None:
        self.age += dt
        if self.age >= self.ptype.max_age:
            self.dead = True
            return

        decay = max(0.05, 1.0 - self.age / self.ptype.max_age)
        rate = self.ptype.base_growth * self.quality * decay * self.viral_mult
        if random.random() < rate * dt:
            self.likes += random.randint(1, 15)
            self.shares += random.randint(0, 4)
            self.comments += random.randint(0, 5)

        if self.viral_flash > 0:
            self.viral_flash = max(0.0, self.viral_flash - dt)


@dataclass
class SocialMediaNotification:
    text: str
    timer: float
    color: tuple[int, int, int]


class SocialMediaGameOverlay(ComputerWindowOverlay):
    """A social feed mini game embedded inside the computer window."""

    def __init__(
        self,
        layout: GameLayout,
        on_close: Callable[[], None],
        energy: Optional[PlayerEnergy] = None,
        music: Optional[BackgroundMusicPlaylist] = None,
    ) -> None:
        self._social_ready = False
        self.energy_state = energy if energy is not None else PlayerEnergy(10, 10)
        self.followers = 100
        self.day = 1
        self.day_timer = 0.0
        self.day_length = 60.0
        self.posts_made = 0
        self.viral_count = 0
        self.eco_impact = 0
        self.total_likes = 0
        self.milestone_index = 0
        self._followers_fraction = 0.0
        self.posts: list[SocialMediaPost] = []
        self.notifications: list[SocialMediaNotification] = []
        self.post_types: list[SocialMediaPostType] = list(SocialMediaPostType)
        self.scroll = 0.0
        self.composing = False
        self.hover_idx = -1
        self.sidebar_post_button: Optional[SpriteButtonPanel] = None
        self.compose_buttons: list[SpriteButtonPanel] = []
        self.sidebar_title_text = arcade.Text(
            "creator stats",
            0,
            0,
            SOCIAL_MEDIA_CARD_TEXT,
            layout.ss(18),
            font_name=UI_FONT_NAME,
            anchor_x="left",
            anchor_y="center",
        )
        self.feed_title_text = arcade.Text(
            "your feed",
            0,
            0,
            SOCIAL_MEDIA_CARD_MUTED,
            layout.ss(18),
            font_name=UI_FONT_NAME,
            anchor_x="left",
            anchor_y="center",
        )
        self.empty_title_text = arcade.Text(
            "nothing posted yet ♡",
            0,
            0,
            SOCIAL_MEDIA_CARD_MUTED,
            layout.ss(18),
            font_name=UI_FONT_NAME,
            anchor_x="center",
            anchor_y="center",
        )
        self.empty_hint_text = arcade.Text(
            "press Space or tap POST to share your first look",
            0,
            0,
            SOCIAL_MEDIA_CARD_MUTED,
            layout.ss(12),
            font_name=UI_FONT_NAME,
            anchor_x="center",
            anchor_y="center",
        )
        self.compose_title_text = arcade.Text(
            "what are you creating today? ♡",
            0,
            0,
            SOCIAL_MEDIA_CARD_TEXT,
            layout.ss(14),
            font_name=UI_FONT_NAME,
            anchor_x="center",
            anchor_y="center",
        )
        self.compose_hint_text = arcade.Text(
            "click a button or press 1-5 ♡ ESC to cancel",
            0,
            0,
            SOCIAL_MEDIA_CARD_MUTED,
            layout.ss(10),
            font_name=UI_FONT_NAME,
            anchor_x="center",
            anchor_y="center",
        )
        super().__init__(layout, "Social Media", on_close, music)
        self._social_ready = True
        self.update_layout(layout)

    @property
    def energy(self) -> int:
        return self.energy_state.current

    @energy.setter
    def energy(self, value: int) -> None:
        self.energy_state.current = max(0, min(value, self.max_energy))

    @property
    def max_energy(self) -> int:
        return self.energy_state.maximum

    @max_energy.setter
    def max_energy(self, value: int) -> None:
        self.energy_state.maximum = max(1, value)
        self.energy_state.current = max(0, min(self.energy_state.current, self.energy_state.maximum))

    def _cooldown_remaining(self, now: Optional[float] = None) -> float:
        current_time = _current_time() if now is None else now
        return max(0.0, self.energy_state.cooldown_ends_at - current_time)

    def _cooldown_active(self, now: Optional[float] = None) -> bool:
        return self._cooldown_remaining(now) > 0.0

    def _format_duration(self, seconds: float) -> str:
        total_seconds = max(0, int(math.ceil(seconds)))
        minutes, remainder = divmod(total_seconds, 60)
        return f"{minutes:02d}:{remainder:02d}"

    def _start_cooldown(self, reason: str, now: Optional[float] = None) -> None:
        current_time = _current_time() if now is None else now
        if self._cooldown_active(current_time):
            return

        self.energy = 0
        self.day_timer = self.day_length
        self.energy_state.cooldown_ends_at = current_time + SOCIAL_MEDIA_COOLDOWN_SECONDS
        self.composing = False
        self.hover_idx = -1
        if reason == "energy":
            self._notify("Out of energy - 10 minute cooldown started ♡", SOCIAL_MEDIA_CARD_MUTED)
        else:
            self._notify("Day finished - 10 minute cooldown started ♡", SOCIAL_MEDIA_CARD_MUTED)

    def _handle_energy_depleted(self) -> None:
        self._notify(
            "Out of energy - keep going until the timer ends ♡",
            SOCIAL_MEDIA_CARD_MUTED,
        )

    def _finish_cooldown(self) -> None:
        self.energy_state.cooldown_ends_at = 0.0
        self.day += 1
        self.day_timer = 0.0
        self.energy = self.max_energy
        self._notify(f"Day {self.day} ♡ energy restored!", (255, 160, 198))

    def _window_size(self, layout: GameLayout) -> tuple[float, float]:
        max_width = max(0.0, layout.width - layout.window_margin * 2)
        max_height = max(0.0, layout.height - layout.window_margin * 2)
        width = min(layout.sx(700), max_width)
        height = min(layout.sy(520), max_height)
        width = max(min(layout.sx(560), max_width), width)
        height = max(min(layout.sy(420), max_height), height)
        return width, height

    def _content_bounds(self) -> tuple[float, float, float, float]:
        left, right, bottom, top = self._bounds()
        return (
            left + self.layout.sx(18),
            right - self.layout.sx(18),
            bottom + self.layout.sy(18),
            top - self.layout.window_header_height - self.layout.sy(16),
        )

    def _sidebar_width(self) -> float:
        content_left, content_right, _, _ = self._content_bounds()
        content_width = max(0.0, content_right - content_left)
        if content_width <= 0.0:
            return 0.0

        min_width = min(self.layout.sx(SOCIAL_MEDIA_SIDEBAR_MIN_WIDTH), content_width)
        max_width = min(self.layout.sx(SOCIAL_MEDIA_SIDEBAR_MAX_WIDTH), content_width)
        return max(
            min_width,
            min(max_width, content_width * 0.34),
        )

    def _feed_bounds(self) -> tuple[float, float, float, float]:
        content_left, content_right, content_bottom, content_top = self._content_bounds()
        sidebar_width = self._sidebar_width()
        feed_left = min(content_right, content_left + sidebar_width + self.layout.sx(18))
        return feed_left, content_right, content_bottom, content_top

    def _sidebar_bounds(self) -> tuple[float, float, float, float]:
        content_left, _, content_bottom, content_top = self._content_bounds()
        sidebar_width = self._sidebar_width()
        return content_left, content_left + sidebar_width, content_bottom, content_top

    def _compose_modal_geometry(self) -> tuple[float, float, float, float]:
        content_left, content_right, content_bottom, content_top = self._content_bounds()
        content_width = content_right - content_left
        content_height = content_top - content_bottom
        width = max(0.0, min(self.layout.sx(SOCIAL_MEDIA_COMPOSE_WIDTH), content_width - self.layout.sx(24)))
        height = max(0.0, min(self.layout.sy(SOCIAL_MEDIA_COMPOSE_HEIGHT), content_height - self.layout.sy(24)))
        left = content_left + (content_width - width) / 2
        bottom = content_bottom + (content_height - height) / 2
        return left, bottom, width, height

    def _compose_button_geometry(self) -> list[tuple[float, float, float, float]]:
        modal_left, modal_bottom, modal_width, modal_height = self._compose_modal_geometry()
        gap = self.layout.sy(8)
        count = len(self.post_types)
        available_height = max(0.0, modal_height - self.layout.sy(70) - (count - 1) * gap)
        button_height = 0.0 if count <= 0 else min(self.layout.sy(58), available_height / count)
        total = count * button_height + (count - 1) * gap
        start_y = modal_bottom + modal_height - self.layout.sy(70) - total
        button_left = modal_left + self.layout.sx(18)
        button_width = max(0.0, modal_width - self.layout.sx(36))
        geometries: list[tuple[float, float, float, float]] = []
        for index in range(count):
            button_bottom = start_y + (count - 1 - index) * (button_height + gap)
            geometries.append((button_left, button_bottom, button_width, button_height))
        return geometries

    def _notify(self, text: str, color: tuple[int, int, int] = SOCIAL_MEDIA_CARD_TEXT) -> None:
        self.notifications.append(SocialMediaNotification(text, 3.5, color))
        if len(self.notifications) > SOCIAL_MEDIA_MAX_NOTIFICATIONS:
            self.notifications.pop(0)

    def _gain_followers(self, count: int) -> None:
        if count <= 0:
            return

        self.followers += count
        while self.milestone_index < len(SOCIAL_MEDIA_MILESTONES):
            threshold, title, subtext = SOCIAL_MEDIA_MILESTONES[self.milestone_index]
            if self.followers < threshold:
                break
            self._notify(f"♡  {title} — {subtext}", SOCIAL_MEDIA_CARD_GOLD)
            self.milestone_index += 1
            self.max_energy = min(20, self.max_energy + 2)

    def _max_scroll(self) -> float:
        _, _, feed_bottom, feed_top = self._feed_bounds()
        content_top = feed_top - self.layout.sy(44)
        content_bottom = feed_bottom + self.layout.sy(12)
        visible_height = max(0.0, content_top - content_bottom)
        total_height = len(self.posts) * self.layout.sy(SOCIAL_MEDIA_CARD_HEIGHT)
        if self.posts:
            total_height += (len(self.posts) - 1) * self.layout.sy(SOCIAL_MEDIA_CARD_GAP)
        return max(0.0, total_height - visible_height)

    def _clamp_scroll(self) -> None:
        self.scroll = max(0.0, min(self.scroll, self._max_scroll()))

    def _create_post(self, ptype: SocialMediaPostType) -> None:
        if self._cooldown_active():
            self._notify(
                f"Cooldown active - wait {self._format_duration(self._cooldown_remaining())} ♡",
                SOCIAL_MEDIA_CARD_MUTED,
            )
            self.composing = False
            return

        if self.energy <= 0:
            self._handle_energy_depleted()
            self.composing = False
            return

        skill = min(0.8, math.log10(max(10, self.followers)) / 6.0)
        quality = max(
            0.05,
            min(
                1.0,
                random.betavariate(
                    1.0 + skill * 3.0,
                    max(1.2, 4.0 - skill * 2.0),
                ),
            ),
        )
        text = random.choice(SOCIAL_MEDIA_TEMPLATES[ptype])
        post = SocialMediaPost(ptype=ptype, text=text, quality=quality)
        self.posts.insert(0, post)
        self.posts = self.posts[:20]
        self.posts_made += 1
        self.energy -= 1
        self.scroll = 0.0
        self.eco_impact += ptype.eco_points
        quality_label = (
            "serving sustainability ♡"
            if quality > 0.70
            else "pretty decent ♡"
            if quality > 0.40
            else "a little weak..."
        )
        accent = (
            SOCIAL_MEDIA_CARD_LIFE_FILL
            if quality > 0.70
            else SOCIAL_MEDIA_CARD_GOLD
            if quality > 0.40
            else SOCIAL_MEDIA_CARD_BORDER
        )
        self._notify(f"Posted  |  {quality_label}  ({quality:.0%})", accent)
        self.composing = False
        self.hover_idx = -1
        if self.energy <= 0:
            self._handle_energy_depleted()

    def _sync_sidebar_controls(self) -> None:
        sidebar_left, sidebar_right, sidebar_bottom, sidebar_top = self._sidebar_bounds()
        button_width = max(0.0, sidebar_right - sidebar_left - self.layout.sx(28))
        button_height = self.layout.sy(38)
        button_center_x = (sidebar_left + sidebar_right) / 2
        button_center_y = max(
            sidebar_bottom + button_height / 2,
            min(sidebar_top - button_height / 2, sidebar_bottom + self.layout.sy(34)),
        )
        if self.sidebar_post_button is None:
            self.sidebar_post_button = SpriteButtonPanel(
                self.layout,
                "POST",
                button_center_x,
                button_center_y,
                button_width,
                button_height,
                (255, 160, 198),
                self._open_compose,
                text_color=(255, 255, 255),
                text_size=self.layout.ss(16),
            )
        else:
            self.sidebar_post_button.update_layout(
                self.layout,
                button_center_x,
                button_center_y,
                button_width,
                button_height,
                self.layout.ss(16),
            )

        geometries = self._compose_button_geometry()
        if not self.compose_buttons:
            for index, ptype in enumerate(self.post_types):
                left, bottom, width, height = geometries[index]
                label = ptype.label
                button = SpriteButtonPanel(
                    self.layout,
                    label,
                    left + width / 2,
                    bottom + height / 2,
                    width,
                    height,
                    ptype.color,
                    lambda ptype=ptype: self._create_post(ptype),
                    text_color=SOCIAL_MEDIA_CARD_TEXT,
                    text_size=self.layout.ss(12),
                )
                self.compose_buttons.append(button)
        else:
            for index, button in enumerate(self.compose_buttons):
                left, bottom, width, height = geometries[index]
                button.update_layout(
                    self.layout,
                    left + width / 2,
                    bottom + height / 2,
                    width,
                    height,
                    self.layout.ss(12),
                )

    def _open_compose(self) -> None:
        if self._cooldown_active():
            self._notify(
                f"Cooldown active - wait {self._format_duration(self._cooldown_remaining())} ♡",
                SOCIAL_MEDIA_CARD_MUTED,
            )
            return
        self.composing = True
        self.hover_idx = -1

    def _close_compose(self) -> None:
        self.composing = False
        self.hover_idx = -1

    def update_layout(self, layout: GameLayout) -> None:
        super().update_layout(layout)
        if not self._social_ready:
            return

        self.window_width, self.window_height = self._window_size(layout)
        self._set_center(layout.width / 2, layout.height / 2 - layout.sy(8))
        self.sidebar_title_text.font_size = layout.ss(18)
        self.feed_title_text.font_size = layout.ss(18)
        self.empty_title_text.font_size = layout.ss(18)
        self.empty_hint_text.font_size = layout.ss(12)
        self.compose_title_text.font_size = layout.ss(14)
        self.compose_hint_text.font_size = layout.ss(10)
        self._sync_sidebar_controls()
        self._clamp_scroll()

    def _draw_sidebar(self) -> None:
        sidebar_left, sidebar_right, sidebar_bottom, sidebar_top = self._sidebar_bounds()
        stripe_width = max(1.0, self.layout.sx(14))
        stripe_count = int(math.ceil((sidebar_right - sidebar_left) / stripe_width))
        for index in range(stripe_count):
            stripe_x = sidebar_left + index * stripe_width
            color = (
                SOCIAL_MEDIA_SIDEBAR_STRIPE_A
                if index % 2 == 0
                else SOCIAL_MEDIA_SIDEBAR_STRIPE_B
            )
            arcade.draw_lrbt_rectangle_filled(
                stripe_x,
                min(sidebar_right, stripe_x + stripe_width),
                sidebar_bottom,
                sidebar_top,
                color,
            )

        arcade.draw_lrbt_rectangle_outline(
            sidebar_left,
            sidebar_right,
            sidebar_bottom,
            sidebar_top,
            SOCIAL_MEDIA_CARD_BORDER,
            2,
        )
        self.sidebar_title_text.x = sidebar_left + self.layout.sx(14)
        self.sidebar_title_text.y = sidebar_top - self.layout.sy(18)
        self.sidebar_title_text.draw()

        follower_label_y = sidebar_top - self.layout.sy(52)
        follower_value_y = follower_label_y - self.layout.sy(30)
        day_label_y = follower_value_y - self.layout.sy(42)
        energy_label_y = day_label_y - self.layout.sy(38)
        cooldown_active = self._cooldown_active()
        now = _current_time()

        arcade.Text(
            "followers",
            sidebar_left + self.layout.sx(18),
            follower_label_y,
            SOCIAL_MEDIA_CARD_MUTED,
            self.layout.ss(10),
            font_name=UI_FONT_NAME,
            anchor_x="left",
            anchor_y="center",
        ).draw()
        arcade.Text(
            _format_compact_count(self.followers),
            sidebar_left + (sidebar_right - sidebar_left) / 2,
            follower_value_y,
            SOCIAL_MEDIA_CARD_TEXT,
            self.layout.ss(32),
            font_name=UI_FONT_NAME,
            anchor_x="center",
            anchor_y="center",
        ).draw()

        progress_x = sidebar_left + self.layout.sx(14)
        progress_y = day_label_y - self.layout.sy(20)
        progress_width = max(0.0, sidebar_right - sidebar_left - self.layout.sx(28))
        if cooldown_active:
            arcade.Text(
                f"cooldown  ♡  {self._format_duration(self._cooldown_remaining(now))} left",
                sidebar_left + (sidebar_right - sidebar_left) / 2,
                day_label_y,
                SOCIAL_MEDIA_CARD_MUTED,
                self.layout.ss(10),
                font_name=UI_FONT_NAME,
                anchor_x="center",
                anchor_y="center",
            ).draw()
        else:
            arcade.Text(
                f"Season {(self.day - 1) // 7 + 1}  ♡  Day {(self.day - 1) % 7 + 1}",
                sidebar_left + (sidebar_right - sidebar_left) / 2,
                day_label_y,
                SOCIAL_MEDIA_CARD_MUTED,
                self.layout.ss(10),
                font_name=UI_FONT_NAME,
                anchor_x="center",
                anchor_y="center",
            ).draw()
        _draw_pill(
            progress_x,
            progress_y,
            progress_width,
            self.layout.sy(10),
            SOCIAL_MEDIA_CARD_LIFE_TRACK,
            SOCIAL_MEDIA_CARD_BORDER,
        )
        if cooldown_active:
            fill_width = min(
                progress_width,
                max(0.0, progress_width * min(1.0, self._cooldown_remaining(now) / SOCIAL_MEDIA_COOLDOWN_SECONDS)),
            )
        else:
            fill_width = min(progress_width, max(0.0, progress_width * min(1.0, self.day_timer / self.day_length)))
        _draw_pill(
            progress_x,
            progress_y,
            fill_width,
            self.layout.sy(10),
            (255, 160, 198),
            (225, 125, 165),
        )

        arcade.Text(
            "energy",
            sidebar_left + (sidebar_right - sidebar_left) / 2,
            energy_label_y,
            SOCIAL_MEDIA_CARD_MUTED,
            self.layout.ss(10),
            font_name=UI_FONT_NAME,
            anchor_x="center",
            anchor_y="center",
        ).draw()
        pip_w = max(0.0, min(self.layout.sx(18), (sidebar_right - sidebar_left - self.layout.sx(24)) / max(1, self.max_energy)))
        total_pips = pip_w * self.max_energy
        start_x = sidebar_left + (sidebar_right - sidebar_left - total_pips) / 2
        pips_y = energy_label_y - self.layout.sy(18)
        for index in range(self.max_energy):
            cx = start_x + (index + 0.5) * pip_w
            fill = (255, 160, 198) if index < self.energy else (255, 229, 238)
            arcade.draw_circle_filled(cx, pips_y, self.layout.ss(5), fill)
            arcade.draw_circle_outline(cx, pips_y, self.layout.ss(5), (225, 125, 165), 1)

        stats_top = pips_y - self.layout.sy(22)
        stats_rows = [
            ("posts made", str(self.posts_made)),
            ("eco impact", str(self.eco_impact)),
            ("active posts", str(len(self.posts))),
            ("total likes", f"{self.total_likes:,}"),
        ]
        row_y = stats_top
        for label, value in stats_rows:
            arcade.Text(
                label,
                sidebar_left + self.layout.sx(14),
                row_y,
                SOCIAL_MEDIA_CARD_MUTED,
                self.layout.ss(10),
                font_name=UI_FONT_NAME,
                anchor_x="left",
                anchor_y="center",
            ).draw()
            arcade.Text(
                value,
                sidebar_right - self.layout.sx(14),
                row_y,
                SOCIAL_MEDIA_CARD_TEXT,
                self.layout.ss(10),
                font_name=UI_FONT_NAME,
                anchor_x="right",
                anchor_y="center",
            ).draw()
            row_y -= self.layout.sy(22)

        if self.sidebar_post_button is not None:
            self.sidebar_post_button.draw()
        arcade.Text(
            "Space or tap POST",
            sidebar_left + (sidebar_right - sidebar_left) / 2,
            sidebar_bottom + self.layout.sy(12),
            SOCIAL_MEDIA_CARD_MUTED,
            self.layout.ss(8),
            font_name=UI_FONT_NAME,
            anchor_x="center",
            anchor_y="center",
        ).draw()

    def _draw_feed(self) -> None:
        feed_left, feed_right, feed_bottom, feed_top = self._feed_bounds()
        if feed_right <= feed_left or feed_top <= feed_bottom:
            return
        arcade.draw_lrbt_rectangle_filled(
            feed_left,
            feed_right,
            feed_bottom,
            feed_top,
            SOCIAL_MEDIA_CONTENT_FILL,
        )
        arcade.draw_lrbt_rectangle_outline(
            feed_left,
            feed_right,
            feed_bottom,
            feed_top,
            SOCIAL_MEDIA_CARD_BORDER,
            2,
        )
        self.feed_title_text.x = feed_left + self.layout.sx(8)
        self.feed_title_text.y = feed_top - self.layout.sy(16)
        self.feed_title_text.draw()
        arcade.draw_line(
            feed_left,
            feed_top - self.layout.sy(28),
            feed_right,
            feed_top - self.layout.sy(28),
            SOCIAL_MEDIA_CARD_BORDER,
            1,
        )

        if not self.posts:
            self.empty_title_text.x = (feed_left + feed_right) / 2
            self.empty_title_text.y = (feed_bottom + feed_top) / 2 + self.layout.sy(18)
            self.empty_title_text.draw()
            self.empty_hint_text.x = (feed_left + feed_right) / 2
            self.empty_hint_text.y = (feed_bottom + feed_top) / 2 - self.layout.sy(6)
            self.empty_hint_text.draw()
            return

        card_height = self.layout.sy(SOCIAL_MEDIA_CARD_HEIGHT)
        card_gap = self.layout.sy(SOCIAL_MEDIA_CARD_GAP)
        content_top = feed_top - self.layout.sy(44)
        content_bottom = feed_bottom + self.layout.sy(12)
        y = content_top + self.scroll
        try:
            window = arcade.get_window()
        except RuntimeError:
            window = None

        previous_scissor = window.ctx.scissor if window is not None else None
        if window is not None:
            window.ctx.scissor = (
                int(feed_left),
                int(content_bottom),
                int(max(0.0, feed_right - feed_left)),
                int(max(0.0, content_top - content_bottom)),
            )
        try:
            for slot, post in enumerate(self.posts):
                self._draw_post_card(
                    post,
                    feed_left + self.layout.sx(4),
                    y - card_height,
                    max(0.0, feed_right - feed_left - self.layout.sx(8)),
                    card_height,
                    slot,
                )
                y -= card_height + card_gap
        finally:
            if window is not None:
                window.ctx.scissor = previous_scissor

    def _draw_post_card(
        self,
        post: SocialMediaPost,
        x: float,
        y: float,
        width: float,
        height: float,
        slot: int,
    ) -> None:
        bar_fill, bar_border, dot_color = post.ptype.bar
        bar_height = self.layout.sy(22)
        pad_x = self.layout.sx(12)
        inner_width = max(0.0, width - pad_x * 2)
        body_fill = SOCIAL_MEDIA_CARD_FILL
        if post.viral_flash > 0:
            body_fill = _lerp_color(SOCIAL_MEDIA_CARD_FILL, bar_fill, min(1.0, (post.viral_flash % 0.4) / 0.4 * 0.25))

        shadow_offset = self.layout.sx(3)
        arcade.draw_lrbt_rectangle_filled(
            x + shadow_offset,
            x + width + shadow_offset,
            y - shadow_offset,
            y + height - shadow_offset,
            (217, 192, 218),
        )
        arcade.draw_lrbt_rectangle_filled(x, x + width, y, y + height, body_fill)
        arcade.draw_lrbt_rectangle_outline(x, x + width, y, y + height, bar_border, 2)
        arcade.draw_lrbt_rectangle_filled(x, x + width, y + height - bar_height, y + height, bar_fill)
        arcade.draw_line(x, y + height - bar_height, x + width, y + height - bar_height, bar_border, 1)
        for index in range(3):
            dot_x = x + self.layout.sx(10) + index * self.layout.sx(13)
            dot_y = y + height - bar_height / 2
            arcade.draw_circle_filled(dot_x, dot_y, self.layout.ss(3.5), dot_color)
            arcade.draw_circle_outline(dot_x, dot_y, self.layout.ss(3.5), bar_border, 1)

        arcade.Text(
            post.ptype.label,
            x + width / 2,
            y + height - bar_height / 2,
            SOCIAL_MEDIA_CARD_TEXT,
            self.layout.ss(10),
            font_name=UI_FONT_NAME,
            anchor_x="center",
            anchor_y="center",
            bold=True,
        ).draw()

        if post.is_viral:
            pill_w = self.layout.sx(60)
            pill_h = bar_height - self.layout.sy(6)
            pill_x = x + width - pill_w - self.layout.sx(8)
            pill_y = y + height - bar_height + self.layout.sy(3)
            _draw_pill(pill_x, pill_y, pill_w, pill_h, SOCIAL_MEDIA_CARD_GOLD, (200, 160, 50))
            arcade.Text(
                "VIRAL",
                pill_x + pill_w / 2,
                pill_y + pill_h / 2,
                SOCIAL_MEDIA_CARD_TEXT,
                self.layout.ss(8),
                font_name=UI_FONT_NAME,
                anchor_x="center",
                anchor_y="center",
                bold=True,
                ).draw()

        max_chars = max(28, int(inner_width / max(1.0, self.layout.ss(6.2))))
        short_text = post.text[:max_chars] + ("..." if len(post.text) > max_chars else "")
        arcade.Text(
            short_text,
            x + pad_x,
            y + height - bar_height - self.layout.sy(18),
            SOCIAL_MEDIA_CARD_TEXT,
            self.layout.ss(12),
            font_name=UI_FONT_NAME,
            anchor_x="left",
            anchor_y="center",
        ).draw()

        stars = max(1, round(post.quality * 5))
        arcade.Text(
            "★" * stars + "☆" * (5 - stars),
            x + pad_x,
            y + height - bar_height - self.layout.sy(42),
            SOCIAL_MEDIA_CARD_GOLD,
            self.layout.ss(12),
            font_name=UI_FONT_NAME,
            anchor_x="left",
            anchor_y="center",
        ).draw()

        arcade.draw_line(
            x + self.layout.sx(10),
            y + self.layout.sy(50),
            x + width - self.layout.sx(10),
            y + self.layout.sy(50),
            SOCIAL_MEDIA_CARD_BORDER,
            1,
        )
        stat_font_size = max(self.layout.ss(9), self.layout.ss(10))
        stats_y = y + self.layout.sy(34)
        arcade.Text(
            f"♡ {post.likes:,}",
            x + pad_x,
            stats_y,
            SOCIAL_MEDIA_CARD_MUTED,
            stat_font_size,
            font_name=UI_FONT_NAME,
            anchor_x="left",
            anchor_y="center",
        ).draw()
        arcade.Text(
            f"↺ {post.shares:,}",
            x + width / 2,
            stats_y,
            SOCIAL_MEDIA_CARD_MUTED,
            stat_font_size,
            font_name=UI_FONT_NAME,
            anchor_x="center",
            anchor_y="center",
        ).draw()
        arcade.Text(
            f"✉ {post.comments:,}",
            x + width - pad_x,
            stats_y,
            SOCIAL_MEDIA_CARD_MUTED,
            stat_font_size,
            font_name=UI_FONT_NAME,
            anchor_x="right",
            anchor_y="center",
        ).draw()

        remaining = max(0.0, 1.0 - post.age / post.ptype.max_age)
        track_x = x + self.layout.sx(12)
        track_y = y + self.layout.sy(8)
        track_w = width - self.layout.sx(24)
        _draw_pill(track_x, track_y, track_w, self.layout.sy(8), SOCIAL_MEDIA_CARD_LIFE_TRACK, SOCIAL_MEDIA_CARD_BORDER)
        if remaining > 0.02:
            fill_w = max(self.layout.sx(8), track_w * remaining)
            _draw_pill(track_x, track_y, fill_w, self.layout.sy(8), _lerp_color(SOCIAL_MEDIA_CARD_BORDER, bar_fill, remaining), bar_border)

    def _draw_notifications(self) -> None:
        feed_left, feed_right, feed_bottom, feed_top = self._feed_bounds()
        y = feed_top - self.layout.sy(22)
        for index, notif in enumerate(reversed(self.notifications[-5:])):
            alpha = int(min(1.0, notif.timer) * 255)
            bg_alpha = int(min(1.0, notif.timer) * 210)
            text_width = len(notif.text) * 7 + 28
            _draw_pill(
                feed_right - text_width - self.layout.sx(12),
                y - self.layout.sy(5),
                text_width,
                self.layout.sy(22),
                (255, 230, 240, bg_alpha),
                (235, 185, 210, bg_alpha),
            )
            arcade.Text(
                notif.text,
                feed_right - self.layout.sx(16),
                y + self.layout.sy(5),
                (*notif.color[:3], alpha),
                self.layout.ss(11),
                font_name=UI_FONT_NAME,
                anchor_x="right",
                anchor_y="center",
            ).draw()
            y -= self.layout.sy(28)

    def _draw_compose_modal(self) -> None:
        modal_left, modal_bottom, modal_width, modal_height = self._compose_modal_geometry()
        content_left, content_right, content_bottom, content_top = self._content_bounds()
        arcade.draw_lrbt_rectangle_filled(
            content_left,
            content_right,
            content_bottom,
            content_top,
            SOCIAL_MEDIA_MODAL_OVERLAY,
        )
        arcade.draw_lrbt_rectangle_filled(
            modal_left + self.layout.sx(3),
            modal_left + modal_width + self.layout.sx(3),
            modal_bottom - self.layout.sy(3),
            modal_bottom + modal_height - self.layout.sy(3),
            (217, 192, 218),
        )
        arcade.draw_lrbt_rectangle_filled(
            modal_left,
            modal_left + modal_width,
            modal_bottom,
            modal_bottom + modal_height,
            SOCIAL_MEDIA_CARD_FILL,
        )
        arcade.draw_lrbt_rectangle_outline(
            modal_left,
            modal_left + modal_width,
            modal_bottom,
            modal_bottom + modal_height,
            SOCIAL_MEDIA_WINDOW_BORDER,
            2,
        )

        self.compose_title_text.x = modal_left + modal_width / 2
        self.compose_title_text.y = modal_bottom + modal_height - self.layout.sy(16)
        self.compose_title_text.draw()
        self.compose_hint_text.x = modal_left + modal_width / 2
        self.compose_hint_text.y = modal_bottom + modal_height - self.layout.sy(38)
        self.compose_hint_text.draw()

        geometries = self._compose_button_geometry()
        for index, (button, geometry) in enumerate(zip(self.compose_buttons, geometries)):
            left, bottom, width, height = geometry
            button.draw()
            if self.hover_idx == index:
                arcade.draw_lrbt_rectangle_outline(
                    left,
                    left + width,
                    bottom,
                    bottom + height,
                    button.fill_color,
                    3,
                )

    def on_update(self, delta_time: float) -> None:
        if not self._social_ready:
            return

        dt = min(delta_time, 0.1)
        now = _current_time()
        if self.energy_state.cooldown_ends_at > 0.0:
            if self._cooldown_remaining(now) <= 0.0:
                self._finish_cooldown()
            else:
                return
        else:
            self.day_timer += dt
            if self.day_timer >= self.day_length:
                self._start_cooldown("day", now)
                return

        total_rate = 0.0
        for post in self.posts:
            post.tick(dt)
            if post.dead:
                continue
            if not post.is_viral and random.random() < post.ptype.viral_chance * dt:
                post.is_viral = True
                post.viral_mult = random.uniform(3.0, 9.0)
                post.viral_flash = 2.5
                self.viral_count += 1
                self._notify(
                    f"♡  {post.ptype.label} went VIRAL! ({post.viral_mult:.1f}x)",
                    SOCIAL_MEDIA_CARD_GOLD,
                )
            total_rate += post.follower_rate

        self._followers_fraction += total_rate * dt
        if self._followers_fraction >= 1.0:
            gained = int(self._followers_fraction)
            self._followers_fraction -= gained
            self._gain_followers(gained)

        if not self.posts and random.random() < 0.0005:
            self.followers = max(0, self.followers - 1)

        self.posts = [post for post in self.posts if not post.dead]
        self.total_likes = sum(post.likes for post in self.posts)
        for notif in self.notifications:
            notif.timer -= dt
        self.notifications = [notif for notif in self.notifications if notif.timer > 0]
        self._clamp_scroll()

    def on_draw(self) -> None:
        super().on_draw()
        content_left, content_right, content_bottom, content_top = self._content_bounds()
        arcade.draw_lrbt_rectangle_filled(
            content_left,
            content_right,
            content_bottom,
            content_top,
            SOCIAL_MEDIA_CONTENT_FILL,
        )
        arcade.draw_lrbt_rectangle_outline(
            content_left,
            content_right,
            content_bottom,
            content_top,
            SOCIAL_MEDIA_CARD_BORDER,
            2,
        )
        self._draw_sidebar()
        self._draw_feed()
        self._draw_notifications()
        if self.composing:
            self._draw_compose_modal()

    def on_key_press(self, key: int, modifiers: int) -> None:
        if self._cooldown_active() and key != arcade.key.ESCAPE:
            return

        if key == arcade.key.ESCAPE:
            if self.composing:
                self._close_compose()
            else:
                self._close()
            return

        if self.composing:
            key_map = {
                arcade.key.KEY_1: 0,
                arcade.key.KEY_2: 1,
                arcade.key.KEY_3: 2,
                arcade.key.KEY_4: 3,
                arcade.key.KEY_5: 4,
            }
            if key in key_map and key_map[key] < len(self.post_types):
                self._create_post(self.post_types[key_map[key]])
            return

        if key == arcade.key.SPACE:
            self._open_compose()
        elif key == arcade.key.UP:
            self.scroll = max(0.0, self.scroll - 100)
        elif key == arcade.key.DOWN:
            self.scroll = min(self._max_scroll(), self.scroll + 100)

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int) -> bool:
        if button != arcade.MOUSE_BUTTON_LEFT:
            return False

        if self._cooldown_active():
            return super().on_mouse_press(x, y, button, modifiers)

        if self.composing:
            _, _, _, content_top = self._content_bounds()
            if y > content_top:
                return super().on_mouse_press(x, y, button, modifiers)
            for index, button_panel in enumerate(self.compose_buttons):
                if button_panel.hit_test(x, y):
                    button_panel.press()
                    self.hover_idx = index
                    return True
            return True

        if self.sidebar_post_button is not None and self.sidebar_post_button.hit_test(x, y):
            self.sidebar_post_button.press()
            return True

        return super().on_mouse_press(x, y, button, modifiers)

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int) -> None:
        if button != arcade.MOUSE_BUTTON_LEFT:
            return

        if self._cooldown_active():
            super().on_mouse_release(x, y, button, modifiers)
            return

        if self.sidebar_post_button is not None:
            self.sidebar_post_button.release()
        for button_panel in self.compose_buttons:
            button_panel.release()
        super().on_mouse_release(x, y, button, modifiers)

    def on_mouse_scroll(self, x: float, y: float, scroll_x: float, scroll_y: float) -> bool:
        if self._cooldown_active():
            return super().on_mouse_scroll(x, y, scroll_x, scroll_y)

        if self.composing:
            return True

        self.scroll = max(0.0, min(self._max_scroll(), self.scroll - scroll_y * 35))
        return True

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float) -> None:
        if self._cooldown_active():
            return super().on_mouse_motion(x, y, dx, dy)

        if not self.composing:
            self.hover_idx = -1
            return

        for index, (left, bottom, width, height) in enumerate(self._compose_button_geometry()):
            if left <= x <= left + width and bottom <= y <= bottom + height:
                self.hover_idx = index
                return
        self.hover_idx = -1

    def on_resize(self, width: float, height: float) -> None:
        self.update_layout(GameLayout(width, height))


class ActivityWindowOverlay(ComputerWindowOverlay):
    """An activity chooser embedded inside a computer-style window."""

    def __init__(
        self,
        layout: GameLayout,
        on_close: Callable[[], None],
        on_open_thrifting: Callable[[], None],
        music: Optional[BackgroundMusicPlaylist] = None,
    ) -> None:
        self._activity_ready = False
        self.upcycling_button = None
        self.thrifting_button = None
        self._selected_label = "Choose an activity"
        self.on_open_thrifting = on_open_thrifting
        self.selection_text = arcade.Text(
            "Choose an activity",
            0,
            0,
            THEME_TEXT_PURPLE,
            layout.ss(18),
            font_name=UI_FONT_NAME,
            anchor_x="center",
            anchor_y="center",
        )
        super().__init__(layout, "Activities", on_close, music)
        self._activity_ready = True
        self._apply_activity_layout(layout)

    def _select_activity(self, label: str) -> None:
        self._selected_label = f"Selected: {label}"
        self.selection_text.text = self._selected_label

    def _apply_activity_layout(self, layout: GameLayout) -> None:
        left, right, bottom, top = self._bounds()
        content_left = left + layout.sx(24)
        content_right = right - layout.sx(24)
        content_top = top - layout.window_header_height - layout.sy(14)
        content_bottom = bottom + layout.sy(22)
        button_width = content_right - content_left
        gap = layout.sy(14)
        max_button_height = (content_top - content_bottom - gap - layout.sy(34)) / 2
        button_height = max(layout.sy(64), min(layout.sy(96), max_button_height))
        first_center_y = content_top - button_height / 2 - layout.sy(10)
        second_center_y = first_center_y - button_height - gap
        button_center_x = (left + right) / 2
        if self.upcycling_button is None:
            self.upcycling_button = SpriteButtonPanel(
                layout,
                "Upcycling Station",
                button_center_x,
                first_center_y,
                button_width,
                button_height,
                (248, 214, 233),
                lambda: self._select_activity("Upcycling Station"),
                text_size=layout.ss(24),
            )
        else:
            self.upcycling_button.update_layout(
                layout,
                button_center_x,
                first_center_y,
                button_width,
                button_height,
                layout.ss(24),
            )
        if self.thrifting_button is None:
            self.thrifting_button = SpriteButtonPanel(
                layout,
                "Thrifting",
                button_center_x,
                second_center_y,
                button_width,
                button_height,
                (214, 238, 222),
                self.on_open_thrifting,
                image_path=THRIFTING_BUTTON_IMAGE_PATH,
                crop_image_to_fit=True,
                text_size=layout.ss(24),
            )
        else:
            self.thrifting_button.update_layout(
                layout,
                button_center_x,
                second_center_y,
                button_width,
                button_height,
                layout.ss(24),
            )
        self.selection_text.x = button_center_x
        self.selection_text.y = bottom + layout.sy(38)
        self.selection_text.font_size = layout.ss(18)

    def update_layout(self, layout: GameLayout) -> None:
        super().update_layout(layout)
        if not self._activity_ready:
            return
        self._apply_activity_layout(layout)

    def on_draw(self) -> None:
        super().on_draw()
        self.selection_text.draw()
        if self.upcycling_button is not None:
            self.upcycling_button.draw()
        if self.thrifting_button is not None:
            self.thrifting_button.draw()

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int) -> bool:
        if button != arcade.MOUSE_BUTTON_LEFT:
            return False
        if self.upcycling_button is not None and self.upcycling_button.hit_test(x, y):
            self.upcycling_button.press()
            return True
        if self.thrifting_button is not None and self.thrifting_button.hit_test(x, y):
            self.thrifting_button.press()
            return True
        return super().on_mouse_press(x, y, button, modifiers)

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int) -> None:
        if button != arcade.MOUSE_BUTTON_LEFT:
            return
        if self.upcycling_button is not None:
            self.upcycling_button.release()
        if self.thrifting_button is not None:
            self.thrifting_button.release()
        super().on_mouse_release(x, y, button, modifiers)

    def on_resize(self, width: float, height: float) -> None:
        self.update_layout(GameLayout(width, height))


@dataclass
class ThriftItem:
    texture_path: Path
    sprite: arcade.Sprite
    price: int
    value: int
    fabric: str
    eco: bool

    @classmethod
    def create(cls) -> "ThriftItem":
        texture_path = random.choice(THRIFTING_CLOTHING_IMAGE_PATHS)
        sprite = arcade.Sprite(texture_path)
        if random.random() < 0.5:
            fabric = random.choice(FAST_FASHION_FABRICS)
            eco = False
            price = random.randint(4, 16)
            value = random.randint(10, 40)
            sprite.color = THRIFTING_WINDOW_FILL
        else:
            fabric = random.choice(ECO_FABRICS)
            eco = True
            price = random.randint(10, 28)
            value = random.randint(30, 70)
            sprite.color = THRIFTING_CONTENT_BORDER
        sprite.alpha = 255
        return cls(texture_path, sprite, price, value, fabric, eco)


class ThriftingGameOverlay(ComputerWindowOverlay):
    """A windowed thrift browsing game with buy-and-score mechanics."""

    def __init__(
        self,
        layout: GameLayout,
        on_close: Callable[[], None],
        wallet: PlayerWallet,
        progress: PlayerProgress,
        music: Optional[BackgroundMusicPlaylist] = None,
    ) -> None:
        self._game_ready = False
        self.rack: list[ThriftItem] = []
        self.sprite_list = arcade.SpriteList()
        self.background_sprite = DrawableSprite(
            _make_sprite(
                THRIFTING_BACKGROUND_IMAGE_PATH,
                layout.width / 2,
                layout.height / 2,
                layout.width,
                layout.height,
                THRIFTING_CONTENT_FILL,
            )
        )
        self.current_index = 0
        self.wallet = wallet
        self.progress = progress
        self.score = 0
        self.message = ""
        self._layout_ready = layout
        self.info_box = ThriftInfoBox(
            layout,
            layout.sx(156),
            layout.height - layout.sy(110),
            layout.ss(250),
            layout.ss(140),
        )
        self.money_text = arcade.Text(
            "",
            0,
            0,
            THRIFTING_TITLE_COLOR,
            layout.ss(16),
            font_name=UI_FONT_NAME,
            anchor_x="left",
            anchor_y="center",
        )
        self.score_text = arcade.Text(
            "",
            0,
            0,
            THRIFTING_TITLE_COLOR,
            layout.ss(16),
            font_name=UI_FONT_NAME,
            anchor_x="left",
            anchor_y="center",
        )
        self.instructions_text = arcade.Text(
            "Left/Right browse   Space buy   Esc back",
            0,
            0,
            THRIFTING_WARNING_COLOR,
            layout.ss(14),
            font_name=UI_FONT_NAME,
            anchor_x="left",
            anchor_y="center",
        )
        self.message_text = arcade.Text(
            "",
            0,
            0,
            THRIFTING_TITLE_COLOR,
            layout.ss(16),
            font_name=UI_FONT_NAME,
            anchor_x="center",
            anchor_y="center",
        )
        super().__init__(layout, "Thrifting", on_close, music)
        self._game_ready = True
        self.setup()
        self.update_layout(layout)

    @property
    def money(self) -> int:
        return self.wallet.amount

    @money.setter
    def money(self, value: int) -> None:
        self.wallet.amount = value

    def _sync_background(self) -> None:
        content_left, content_right, content_bottom, content_top = self._content_bounds()
        self.background_sprite.center_x = (content_left + content_right) / 2
        self.background_sprite.center_y = (content_bottom + content_top) / 2
        self.background_sprite.width = content_right - content_left
        self.background_sprite.height = content_top - content_bottom

    def _thrifting_window_size(self, layout: GameLayout) -> tuple[float, float]:
        """Size the thrifting window so the canvas matches the art's aspect ratio."""
        horizontal_padding = layout.sx(36)
        vertical_padding = layout.sy(34)
        header_height = layout.window_header_height
        max_window_width = layout.width - layout.window_margin * 2
        max_window_height = layout.height - layout.window_margin * 2

        max_content_width = max(0.0, max_window_width - horizontal_padding)
        max_content_height = max(0.0, max_window_height - header_height - vertical_padding)

        if max_content_width / THRIFTING_ART_ASPECT_RATIO <= max_content_height:
            content_width = max_content_width
            content_height = content_width / THRIFTING_ART_ASPECT_RATIO
        else:
            content_height = max_content_height
            content_width = content_height * THRIFTING_ART_ASPECT_RATIO

        return content_width + horizontal_padding, content_height + header_height + vertical_padding

    def setup(self) -> None:
        self.rack.clear()
        self.sprite_list = arcade.SpriteList()
        self.current_index = 0
        self.score = 0
        self.message = ""
        for _ in range(THRIFTING_RACK_SIZE):
            item = ThriftItem.create()
            self.rack.append(item)
        self._update_positions()
        self._sync_text()

    def _content_bounds(self) -> tuple[float, float, float, float]:
        left, right, bottom, top = self._bounds()
        return (
            left + self.layout.sx(18),
            right - self.layout.sx(18),
            bottom + self.layout.sy(18),
            top - self.layout.window_header_height - self.layout.sy(16),
        )

    def _show_current_item(self) -> None:
        self.sprite_list.clear()
        if not self.rack:
            return
        item = self.rack[self.current_index]
        item.sprite.center_x = self.background_sprite.center_x
        item.sprite.center_y = self.background_sprite.center_y
        item.sprite.width = self.background_sprite.width
        item.sprite.height = self.background_sprite.height
        item.sprite.alpha = 255
        self.sprite_list.append(item.sprite)

    def _update_positions(self) -> None:
        for item in self.rack:
            item.sprite.alpha = 0
        if self.rack:
            self._show_current_item()
        self._sync_text()

    def _sync_text(self) -> None:
        content_left, content_right, content_bottom, content_top = self._content_bounds()
        self.money_text.text = f"Money: ${self.money}"
        self.score_text.text = f"Score: {self.score}"
        self.money_text.color = THRIFTING_TITLE_COLOR
        self.score_text.color = THRIFTING_TITLE_COLOR
        self.instructions_text.color = THRIFTING_WARNING_COLOR
        self.instructions_text.x = content_left
        self.instructions_text.y = content_bottom + self.layout.sy(12)
        self.money_text.x = content_left
        self.money_text.y = content_bottom + self.layout.sy(64)
        self.score_text.x = content_left
        self.score_text.y = content_bottom + self.layout.sy(38)
        self.message_text.x = (content_left + content_right) / 2
        self.message_text.y = min(content_top - self.layout.sy(28), content_bottom + self.layout.sy(80))
        self.message_text.text = self.message
        info_width = min(self.layout.ss(250), (content_right - content_left) * 0.32)
        info_height = min(self.layout.ss(140), content_top - content_bottom - self.layout.sy(24))
        self.info_box.update_layout(
            self.layout,
            content_left + info_width / 2,
            content_top - info_height / 2,
            info_width,
            info_height,
        )
        if self.rack:
            item = self.rack[self.current_index]
            self.info_box.set_item(item)
        else:
            self.info_box.set_item(None)

    def _select_next(self, direction: int) -> None:
        if not self.rack:
            return
        self.current_index = (self.current_index + direction) % len(self.rack)
        self._update_positions()

    def _buy_current_item(self) -> None:
        if not self.rack:
            return
        item = self.rack[self.current_index]
        if item.price > self.money:
            self.message = "Not enough money!"
            self.message_text.color = THRIFTING_WARNING_COLOR
            return
        self.money -= item.price
        levels_gained = 0
        if item.eco:
            delta = (item.value - item.price) * 2
            self.score += delta
            self.message = f"Eco buy +{delta}"
            self.message_text.color = THRIFTING_SUCCESS_COLOR
            levels_gained = self.progress.add_experience(delta)
        else:
            delta = -(item.price + 10)
            experience_lost = -delta
            self.score += delta
            self.message = f"Fast fashion {delta}"
            self.message_text.color = THRIFTING_WARNING_COLOR
            self.progress.add_experience(-experience_lost)

        if levels_gained > 0:
            self.money += levels_gained * THRIFTING_LEVEL_UP_REWARD
            level_word = "level" if levels_gained == 1 else "levels"
            reward = levels_gained * THRIFTING_LEVEL_UP_REWARD
            self.message = f"{self.message}  +${reward} for {levels_gained} {level_word} up"

        self.sprite_list.remove(item.sprite)
        self.rack.pop(self.current_index)
        replacement = ThriftItem.create()
        self.rack.append(replacement)
        if self.current_index >= len(self.rack):
            self.current_index = 0
        self._sync_text()
        self._update_positions()

    def update_layout(self, layout: GameLayout) -> None:
        super().update_layout(layout)
        if not self._game_ready:
            return
        self.window_width, self.window_height = self._thrifting_window_size(layout)
        self._set_center(layout.width / 2, layout.height / 2 - layout.sy(8))
        self._sync_background()
        self.money_text.font_size = layout.ss(16)
        self.score_text.font_size = layout.ss(16)
        self.instructions_text.font_size = layout.ss(14)
        self.message_text.font_size = layout.ss(16)
        self._update_positions()

    def _set_center(self, center_x: float, center_y: float) -> None:
        super()._set_center(center_x, center_y)
        if self._game_ready:
            self._sync_background()

    def on_update(self, delta_time: float) -> None:
        if not self._game_ready:
            return
        self._update_positions()

    def on_draw(self) -> None:
        super().on_draw()
        self.background_sprite.draw()
        self.sprite_list.draw()
        self.info_box.draw()
        self.money_text.draw()
        self.score_text.draw()
        self.instructions_text.draw()
        self.message_text.draw()

    def on_key_press(self, key: int, modifiers: int) -> None:
        if key == arcade.key.ESCAPE:
            self._close()
            return
        if key == arcade.key.LEFT:
            self._select_next(-1)
        elif key == arcade.key.RIGHT:
            self._select_next(1)
        elif key == arcade.key.SPACE:
            self._buy_current_item()

    def on_resize(self, width: float, height: float) -> None:
        self.update_layout(GameLayout(width, height))


def main() -> None:
    """Start the game window."""
    display_width, display_height = arcade.get_display_size()
    window = arcade.Window(
        min(DEFAULT_WINDOW_WIDTH, display_width),
        min(DEFAULT_WINDOW_HEIGHT, display_height),
        SCREEN_TITLE,
        resizable=True,
        center_window=True,
    )
    window.show_view(HomeView())
    arcade.run()


if __name__ == "__main__":
    main()
